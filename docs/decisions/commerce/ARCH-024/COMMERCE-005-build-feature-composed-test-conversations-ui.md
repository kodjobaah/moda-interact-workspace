---
id: ARCH-024-COMMERCE-005
architecture_id: ARCH-024
title: Build Feature-composed Test Conversations UI
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 50
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-024-COMMERCE-002
  - ARCH-024-COMMERCE-004
  - ARCH-023-COMMERCE-003
enables:
  - ARCH-024-COMMERCE-006
created: 2026-09-30
updated: 2026-10-01
---

# Build Feature-composed Test Conversations UI

## Architecture

Architecture ID:

`ARCH-024`

Architecture document:

`docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`

Coordinator:

`moda_architect`

## Objective

Build the new human-facing Test Conversations authoring surface on top of the Feature-composition boundary from ARCH-024-COMMERCE-004.

The UI MUST express exactly this product model:

```text
validated Studio Shop
        +
one effective active Commerce model
        +
ARCH-023 Platform Instructions
        +
optional ARCH-023 Shop Instructions
        +
selected Feature IDs
        |
        v
server creates one Feature-composed Test Conversation snapshot
```

The administrator selects **Features only**. Selecting one Feature means all of that Feature's direct Capabilities participate in the conversation composition. Capabilities and Tools are displayed read-only for explanation; they are never selectable independently.

This task owns the selected-Shop conversation-start contract and the authoring UI only. It MUST NOT implement real selected-Shop Tool execution or OpenRouter model execution. Those remain ARCH-024-COMMERCE-006 and ARCH-024-COMMERCE-007.

## Context

ARCH-024-COMMERCE-001 removes the obsolete human Preview composer. ARCH-024-COMMERCE-004 replaces Release/Draft conversation composition with:

```ts
{
  kind: 'FEATURES',
  featureIds: string[]
}
```

and stores the exact Feature/Capability/Tool/Feature-Behaviour composition in the existing Preview conversation state.

ARCH-023 is frozen. ARCH-023-COMMERCE-003 changes effective Agent Configuration from one overriding Prompt to additive trusted instructions:

```text
Platform Instructions
+ optional Shop Instructions
```

and exposes:

```ts
EffectiveAgentConfiguration.instructions = {
  platform: EffectivePrompt;
  shop: EffectivePrompt | null;
  ordered: Array<{
    source: 'PLATFORM' | 'PRICING_PLAN' | 'SHOP';
    revisionId: string;
    text: string;
  }>;
};
```

ARCH-024-COMMERCE-002 establishes the one-effective-active-model resolver used by this task. COMMERCE-003 is an independent Studio ownership-cutover UI and is deliberately not a prerequisite. By the time this task executes, `getEffectiveAgentConfiguration(shopId)` from C002 is the authoritative read for the selected Shop's effective Model plus ARCH-023 instruction provenance.

The current Preview UI must not be reconstructed. There is no Tool mode, Release/Draft mode, fixture selector, model-mode selector, Release handoff or Capability selector in the replacement UI.

ARCH-024 is pre-production. No browser compatibility is required with the old human Preview request shape.

## Scope

Primary implementation surface:

```text
moda-interact-commerce/app/preview/page.tsx
moda-interact-commerce/src/studio/test-conversations/contracts.ts               # create
moda-interact-commerce/src/studio/test-conversations/test-conversations-screen.tsx
moda-interact-commerce/src/studio/test-conversations/client.ts                    # create
moda-interact-commerce/src/commerce/preview/types.ts
moda-interact-commerce/src/commerce/preview/service.ts
moda-interact-commerce/src/commerce/integration/preview/adapters.ts

moda-interact-commerce/tests/test-conversations-screen.test.tsx
moda-interact-commerce/tests/test-conversations-client.test.ts
moda-interact-commerce/tests/preview-routes.test.ts
moda-interact-commerce/tests/preview-service.test.ts
```

A focused page test may be created at exactly:

```text
moda-interact-commerce/tests/preview-page.test.tsx
```

if `app/preview/page.tsx` loading/projection coverage is materially clearer there.

Create one focused server snapshot test at exactly:

```text
moda-interact-commerce/tests/test-conversation-snapshot.test.ts
```

Additional Commerce files may change only when mechanically required by the exact selected-Shop conversation-start contract defined below. Every additional file MUST be listed and justified in the Completion Report.

Do not modify:

```text
moda-interact-commerce/database/**
moda-interact-shared/**
moda-interact-admin/**
moda-interact-background/**
moda-interact-gateway/**
```

## Out of Scope

- Real Shopify/External/Policy Tool execution against the selected Shop; ARCH-024-COMMERCE-006 owns it.
- OpenRouter/LangChain model execution; ARCH-024-COMMERCE-007 owns it.
- Reading/decrypting an OpenRouter credential.
- Changing active Model selection.
- Model Catalogue or Model Availability administration.
- Platform/Shop Instruction mutation.
- Capability-local authoring.
- Per-Capability inclusion/exclusion.
- Release creation/activation/selection.
- Billing/plan/merchant-preference filtering of selected Features.
- Reintroducing Fixture Scenario or FIXTURE/MODEL product controls.
- Removing the retained low-level Tool-test fixture API used by Tool Authoring / Code Response.
- LangGraph adoption.
- Database or Shared-package changes.

## Requirements

### R1 — create one bounded Test Conversation UI contract

Create:

```text
src/studio/test-conversations/contracts.ts
```

with exactly these browser-safe UI contracts:

```ts
export type TestConversationCapabilityOption = {
  id: string;
  key: string;
  displayName: string;
  description: string;
  enabled: boolean;
  tool: {
    id: string;
    name: string;
    displayName: string;
    enabled: boolean;
  };
};

export type TestConversationFeatureOption = {
  id: string;
  key: string;
  displayName: string;
  active: boolean;
  capabilities: TestConversationCapabilityOption[];
};

export type TestConversationConfigurationSummary = {
  shop: {
    id: string;
    domain: string;
    label: string;
    plan: string;
    shopifyOfflineSessionAvailable: boolean;
  };
  model: {
    source: 'PLATFORM' | 'PRICING_PLAN' | 'SHOP';
    id: string;
    displayName: string;
    provider: string;
    providerModelId: string;
  };
  instructions: {
    platform: {
      revisionId: string;
      revisionNumber: number;
    };
    shop: {
      revisionId: string;
      revisionNumber: number;
    } | null;
  };
};

export type TestConversationConfigurationState =
  | { kind: 'NO_SHOP' }
  | { kind: 'UNAVAILABLE'; message: string }
  | { kind: 'READY'; value: TestConversationConfigurationSummary };
```

The browser-facing configuration summary MUST NOT contain:

```text
Platform Instruction text
Shop Instruction text
OpenRouter credential material
Model configuration JSON
Shopify access token/session body
External connection credentials
Feature Behaviour text
Tool definitions
```

This UI task needs provenance/identity for display, not trusted instruction/model secret payloads.

### R2 — project Feature authoring data to the exact UI shape

`app/preview/page.tsx` MUST obtain Feature data through the accepted existing Studio Feature read path (`listFeatureAuthoring()` or the accepted equivalent after prior tasks).

Before crossing the Server Component -> Client Component boundary, project each Feature to `TestConversationFeatureOption` exactly:

```text
Feature.id                  -> id
Feature.key                 -> key
Feature.displayName         -> displayName
Feature.active              -> active

Capability.id               -> capabilities[].id
Capability.key              -> capabilities[].key
Capability.displayName      -> capabilities[].displayName
Capability.description      -> capabilities[].description
Capability.enabled          -> capabilities[].enabled
Capability.tool.id          -> capabilities[].tool.id
Capability.tool.name        -> capabilities[].tool.name
Capability.tool.displayName -> capabilities[].tool.displayName
Capability.tool.enabled     -> capabilities[].tool.enabled
```

Do NOT pass these authoring fields into the browser for this page:

```text
Feature.behaviourPrompt
Feature.editVersion
Capability.updatedAt
```

Feature order in the UI MUST be deterministic:

```text
Feature.displayName ascending using localeCompare
then Feature.id ascending
```

Capability order within each Feature MUST be:

```text
Capability.key ascending
then Capability.id ascending
```

This display order does not redefine ARCH-024-COMMERCE-004 composition order. The selected `featureIds` order submitted by the UI is the order in which the user selected them, as required by R8.

### R3 — selected Studio Shop is authoritative

`app/preview/page.tsx` MUST continue to call:

```ts
resolveStudioShopSelection(query.shopId)
```

and MUST treat only:

```ts
shopSelection.selectedShop
```

as the selected Shop.

Never pass the raw `searchParams.shopId` through to Preview execution after validation failed.

When no validated Shop is selected:

```ts
configurationState = { kind: 'NO_SHOP' }
```

The Feature catalogue MAY still be displayed, but Start Conversation MUST remain disabled.

### R4 — resolve and project one effective Agent Configuration

When a validated Shop is selected, `app/preview/page.tsx` MUST call the accepted effective configuration read:

```ts
getEffectiveAgentConfiguration(selectedShop.id)
```

After ARCH-023-COMMERCE-003 and ARCH-024-COMMERCE-002, a Test Conversation is startable only when all of these are true:

```text
effective model source = PLATFORM, PRICING_PLAN or SHOP
effective model.model != null
Platform Instructions are valid/published
optional Shop Instructions, when present, are valid/published
```

Map the effective read to `TestConversationConfigurationSummary`.

The UI summary MUST contain only:

```text
selected Shop identity
model identity + display metadata + selection source
Platform Instruction revision identity/number
optional Shop Instruction revision identity/number
```

If the effective read is unavailable/broken, map it to:

```ts
{
  kind: 'UNAVAILABLE',
  message: 'The selected shop does not have a usable CommerceAgent configuration.'
}
```

Do not expose raw database/provider failure detail.

### R5 — exact selected-Shop conversation start request

Replace the browser-facing Conversation start body with exactly:

```ts
{
  previewConversationId: string;
  shopId: string;
  selection: {
    kind: 'FEATURES';
    featureIds: string[];
  };
}
```

Accordingly, `ConversationBodySchema` MUST become exactly:

```ts
export const ConversationBodySchema = z.strictObject({
  previewConversationId: PreviewIdSchema,
  shopId: SavedIdSchema,
  selection: PreviewSelectionSchema,
});
```

The human Conversation boundary MUST NOT accept:

```text
mode
fixtureId
externalResponseFixtures
releaseId
capabilityIds
toolRevisionIds
responseContract
```

Do not change the independent `ToolTestBodySchema`; Tool Authoring/Code Response fixture-backed Tool testing remains a separate retained boundary.

### R6 — server revalidates the Shop; browser shopId is never authoritative

The POST `/api/studio/preview/conversations` path MUST NOT trust `shopId` solely because the Server Component previously resolved it.

Before building/storing the Feature composition, the Preview server integration MUST resolve the exact current Shop through the accepted server-side Studio Shop execution-context read and require the requested `shopId` to resolve successfully.

Expected mapping:

```text
unknown/unavailable Shop -> NOT_FOUND or UNAVAILABLE using existing bounded Preview errors
authorization failure    -> DENIED/FORBIDDEN through existing mapping
```

Do not accept Shop domain, plan, Shopify session availability or any other Shop metadata from the browser body.

### R7 — C005 owns the complete authored Conversation Configuration Snapshot

The Feature composition returned by ARCH-024-COMMERCE-004 is a server-side composition fragment. This task is the **single owner** that turns that fragment into the complete human Test Conversation authored snapshot when Start Conversation commits.

Extend the Feature-composed Preview bundle-loading boundary from ARCH-024-COMMERCE-004 so the exact selected Shop ID is an explicit input:

```ts
interface PreviewBundleLoader {
  load(input: {
    principal: PreviewPrincipal;
    shopId: string;
    selection: PreviewSelection;
  }): Promise<PreviewBundle | PreviewLoadedBundle>;
}
```

For the Feature-composed conversation:

```text
PreviewBundle.grant.shopId = validated selected Shop.id
```

The grant MUST NOT use a synthetic `preview-<admin>` Shop ID for an ARCH-024 Feature Test Conversation.

In `src/commerce/preview/types.ts`, define the complete authored snapshot from the same raw composition fields as C004. The current baseline applies `.superRefine(...)` directly to `PreviewFrozenSnapshotSchema`; do **not** depend on calling `.extend(...)` on that refined schema. Refactor the existing schema mechanically so one reusable base object plus one shared composition-refinement function backs both schemas:

```ts
const PreviewFrozenSnapshotBaseSchema = z.strictObject({
  definitions: z.array(z.strictObject({
    revisionId: SavedIdSchema,
    definition: z.unknown(),
  })).max(32),
  prompts: PreviewPromptsSchema,
});

function validateFrozenSnapshotComposition(
  value: { definitions: Array<{ revisionId: string; definition: unknown }>; prompts: PreviewPrompt[] },
  context: z.RefinementCtx,
): void {
  // Move the existing PreviewFrozenSnapshotSchema superRefine body here unchanged:
  // - definition <= 65,536 bytes
  // - authored prompt text <= 64,000 characters
  // - composition/frozen snapshot <= 3 MiB
}

export const PreviewFrozenSnapshotSchema =
  PreviewFrozenSnapshotBaseSchema.superRefine(validateFrozenSnapshotComposition);

export const PreviewConversationShopSnapshotSchema = z.strictObject({
  id: SavedIdSchema,
  domain: z.string().trim().min(1).max(255),
});

export type PreviewConversationShopSnapshot =
  z.infer<typeof PreviewConversationShopSnapshotSchema>;

export const PreviewConversationModelSnapshotSchema = z.strictObject({
  selectionSource: CommerceModelSelectionSourceSchema,
  merchantPricingPlanId: SavedIdSchema.nullable(),
  shopifyPlanHandle: z.string().trim().min(1).max(255).nullable(),
  catalogueEntryId: SavedIdSchema,
  provider: CommerceModelProviderSchema,
  providerModelId: CommerceProviderModelIdSchema,
  configurationSchemaVersion: z.number().int().positive(),
  configuration: CommerceModelConfigurationSchema,
}).superRefine((value, context) => {
  if (value.selectionSource === 'PRICING_PLAN') {
    if (value.merchantPricingPlanId === null || value.shopifyPlanHandle === null) {
      context.addIssue({ code: 'custom', message: 'price plan model provenance is incomplete' });
    }
    return;
  }
  if (value.merchantPricingPlanId !== null || value.shopifyPlanHandle !== null) {
    context.addIssue({ code: 'custom', message: 'non-price-plan model has price plan provenance' });
  }
});

export type PreviewConversationModelSnapshot =
  z.infer<typeof PreviewConversationModelSnapshotSchema>;

export const PreviewInstructionRevisionSnapshotSchema = z.strictObject({
  revisionId: SavedIdSchema,
  revisionNumber: z.number().int().positive(),
  text: z.string().trim().min(1).max(32_000),
});

export const PreviewConversationInstructionsSnapshotSchema = z.strictObject({
  platform: PreviewInstructionRevisionSnapshotSchema,
  shop: PreviewInstructionRevisionSnapshotSchema.nullable(),
});

export const PreviewConversationSnapshotSchema =
  PreviewFrozenSnapshotBaseSchema.extend({
    shop: PreviewConversationShopSnapshotSchema,
    model: PreviewConversationModelSnapshotSchema,
    instructions: PreviewConversationInstructionsSnapshotSchema,
  }).superRefine(validateFrozenSnapshotComposition);

export type PreviewConversationSnapshot =
  z.infer<typeof PreviewConversationSnapshotSchema>;
```

For the human Feature Test Conversation, `StoredConversation.snapshot` MUST use `PreviewConversationSnapshot`. Do not add a parallel `StoredConversation.shop`, `StoredConversation.model` or `StoredConversation.instructions` authored-state object.

The retained fixture-backed Tool-test boundary MAY continue using the narrower `PreviewFrozenSnapshot` where required. Do not force independent Tool-test fixtures to carry Shop/model/instruction state.

The Start transaction/operation MUST perform this sequence from server-owned reads only:

```text
1. revalidate requested shopId through the accepted Studio Shop execution-context read
2. load the C004 Feature composition for the exact ordered featureIds
3. resolve the selected Shop's effective Agent Configuration through the accepted C002/ARCH-023 server read
4. validate that the effective model source is SHOP, PRICING_PLAN or PLATFORM and model != null
5. validate provider/providerModelId/configuration through the published Shared model schemas
6. require valid Platform Instructions and valid optional Shop Instructions
7. assemble PreviewConversationSnapshot exactly once
8. validate the complete snapshot before storing/claiming the conversation
```

Map the Shop snapshot only from the accepted server-side Shop result:

```text
selectedShop.id     -> snapshot.shop.id
selectedShop.domain -> snapshot.shop.domain
```

Never copy Shop domain from URL/query/body data.

Map the model snapshot exactly from the accepted effective model:

```text
selectionSource              -> snapshot.model.selectionSource
merchantPricingPlanId        -> snapshot.model.merchantPricingPlanId
shopifyPlanHandle            -> snapshot.model.shopifyPlanHandle
catalogueEntryId             -> snapshot.model.catalogueEntryId
provider                     -> snapshot.model.provider
providerModelId              -> snapshot.model.providerModelId
configurationSchemaVersion   -> snapshot.model.configurationSchemaVersion
configuration                -> snapshot.model.configuration
```

Enforce provenance exactly:

```text
selectionSource = PRICING_PLAN
    -> merchantPricingPlanId and shopifyPlanHandle are non-null

selectionSource = PLATFORM or SHOP
    -> merchantPricingPlanId and shopifyPlanHandle are null
```

Map ARCH-023 additive trusted instructions exactly from the already-resolved effective configuration:

```text
platform.revisionId      -> snapshot.instructions.platform.revisionId
platform.revisionNumber  -> snapshot.instructions.platform.revisionNumber
platform.text            -> snapshot.instructions.platform.text

shop = null
    when effective instructions.shop = null

otherwise:
shop.revisionId          -> snapshot.instructions.shop.revisionId
shop.revisionNumber      -> snapshot.instructions.shop.revisionNumber
shop.text                -> snapshot.instructions.shop.text
```

If the accepted ARCH-023 effective contract names these resolved fields differently, map the exact accepted equivalents. Do not reread prompt-template source rows after resolving the effective instructions.

The snapshot composition fields remain the exact C004 values:

```text
selection + bundle.manifest
snapshot.definitions
snapshot.prompts
```

The complete snapshot MUST NOT contain live operational state:

```text
OpenRouter credential/ciphertext/nonce/authTag/keyId
Shopify access token/offline-session secret
External HTTP connection credential or resolved auth headers
provider response bodies
```

Those values remain live and are resolved by C006/C007 when needed.

Conversation creation MUST fail bounded `UNAVAILABLE` and MUST NOT persist/claim a conversation when the Shop, Feature composition, effective model or instruction snapshot cannot be validated.

Once Start succeeds, this authored snapshot is immutable for the conversation. C006 and C007 MUST consume it; they MUST NOT extend it with additional authored fields or reread current Shop/model/instruction/Feature/Tool authoring state for an already-started conversation.

### R8 — Feature selection semantics are explicit and stable

The UI MUST render exactly one checkbox per `TestConversationFeatureOption`.

Rules:

```text
Feature with >=1 Capability
    -> checkbox selectable

Feature with 0 Capabilities
    -> checkbox disabled
    -> display "No capabilities"

Feature.active = false
    -> remains selectable
    -> display "Inactive · testable"

Capability.enabled = false
    -> still displayed and included by Feature selection
    -> display "Disabled in production"

Tool.enabled = false
    -> still displayed and included by Feature selection
    -> display "Tool disabled in production"
```

Those status labels are informational only. They MUST NOT recreate production eligibility filtering; ARCH-024-COMMERCE-004 deliberately composes all direct Capabilities for an explicitly selected Feature.

Selected Feature IDs MUST be stored in **user-selection order**:

```text
first checkbox selected  -> featureIds[0]
second checkbox selected -> featureIds[1]
...
```

Unselecting removes that ID without reordering the remaining IDs.

Re-selecting appends the Feature ID to the end.

The client MUST prevent selecting more than 32 Features. When 32 are selected, remaining unchecked selectable Feature checkboxes are disabled until one selection is removed.

The server remains authoritative for the 32-Capability manifest limit and Tool publication readiness.

### R9 — exact page layout and labels

The replacement page title MUST be:

```text
Test conversations
```

The Studio description for `preview` MUST no longer describe synthetic fixtures. Replace the current Preview description with exactly:

```text
Compose a CommerceAgent from selected Features and test that configuration for the selected shop.
```

`TestConversationsScreen` MUST render sections in this order:

```text
1. Agent configuration
2. Features
3. Conversation
```

#### Agent configuration section

When READY, display exactly these labelled facts:

```text
Shop                 <shop.domain>
Plan                 <shop.plan>
Active model         <model.displayName>
Model ID             <provider>/<providerModelId>
Model source         Platform | Price Plan | Shop
Platform Instructions Revision <revisionNumber>
Shop Instructions    Revision <revisionNumber> | None
Shopify session      Available | Unavailable
```

`Shopify session = Unavailable` MUST NOT by itself disable Start Conversation; the selected Feature set may not require a Shopify Tool. Later real Tool execution is responsible for bounded failure when a required Shopify session is absent.

When `NO_SHOP`, show:

```text
Select an Authoring shop before starting a Test Conversation.
```

When `UNAVAILABLE`, show the bounded message from R4.

#### Features section

For every Feature display:

```text
checkbox
Feature display name
Feature key
Feature status, when inactive
```

Under each Feature, display all Capabilities read-only with:

```text
Capability display name
Capability key
Tool display name
Tool name
production-disabled status labels where applicable
```

Do not display/edit Feature Behaviour text on this screen.

#### Conversation section

Before a conversation starts, display:

```text
No Test Conversation has been started.
```

After successful start, display:

```text
Test Conversation started.
Conversation ID: <previewConversationId>
```

and a transcript container prepared for later runtime tasks.

The message textarea and Send button MUST be rendered but disabled in this task with exactly:

```text
Conversation execution is enabled by the remaining ARCH-024 runtime tasks.
```

ARCH-024-COMMERCE-007 owns enabling actual model turns after real Tool/OpenRouter execution is complete.

This deliberate transitional state prevents the new UI from silently using the old synthetic model/tool runtime while ARCH-024 is being implemented.

### R10 — Start Conversation eligibility is deterministic

Start Conversation is enabled only when all are true:

```text
configurationState.kind = READY
selected Feature count >= 1
selected Feature count <= 32
no selected Feature has zero Capabilities
no Start operation is currently pending/unknown
no conversation has already been started in this mounted screen
```

Do NOT require:

```text
Shopify offline session available
Feature.active = true
Capability.enabled = true
Tool.enabled = true
billing/plan eligibility
active Release
```

The server remains authoritative for Feature/Capability/Tool composition readiness and may return bounded NOT_FOUND/UNAVAILABLE.

### R11 — Start Conversation is same-tick single-flight safe

Do not rely only on React state to prevent duplicate starts.

Use an imperative ref gate acquired synchronously before any asynchronous request or React state transition.

Required behaviour:

```text
first click / keyboard activation
    -> create one previewConversationId
    -> freeze one exact payload in the pending-operation ref
    -> dispatch exactly once

second click in same JavaScript tick
    -> no second ID
    -> no second request
```

A test MUST fire Start Conversation multiple times in one `act(...)` block and assert exactly one `startConversation` request.

### R12 — uncertain start outcome preserves the original operation identity

The existing Preview start path is operation-ID/idempotency aware. Preserve that behaviour.

On a transport/uncertain response:

```text
retain the exact original previewConversationId
retain the exact original shopId
retain the exact original ordered featureIds
lock configuration + Feature selection
show "Check original start"
```

The reconciliation action MUST resubmit the **same exact payload**.

It MUST NOT:

```text
generate a new previewConversationId
change selected Feature order
change Shop
start a second conversation
```

Only after the original outcome is known not to have committed may the user return to a fresh Start operation.

### R13 — successful start freezes the authoring controls for that mounted conversation

After `startConversation` succeeds:

```text
Feature checkboxes -> disabled
Start Conversation -> disabled
configuration summary -> read-only
```

Provide exactly one local action:

```text
Start new conversation
```

This action clears only the current browser conversation identity/transcript shell and selected Feature list, returning to the pre-start authoring state.

It MUST NOT attempt to delete persisted Preview/Redis history. Existing bounded Preview retention/expiry owns server cleanup.

Changing the global Studio Authoring shop through the existing Shop selector causes normal navigation/remount and therefore starts a fresh Test Conversation authoring state.

### R14 — do not leak trusted instruction or model configuration text into the browser unnecessarily

The browser needs only provenance/identity described by R1/R4.

Tests MUST prove page/client props do not include:

```text
Platform Instructions text
Shop Instructions text
Model configuration JSON
Feature Behaviour text
Tool definition JSON
OpenRouter credential
Shopify access token
External connection secrets
```

The trusted texts/Tool definitions remain server-side in the composition/runtime state created by earlier/later tasks.

### R15 — do not reintroduce legacy Preview controls

The following strings/controls MUST remain absent from the human Test Conversations surface:

```text
Tool source
Release source
Saved selection
Release
Draft revisions
Fixture scenario
Model mode
FIXTURE
MODEL
Synthetic preview
Test conversation handoff from Release composer
```

Do not add compatibility aliases, hidden selectors or feature flags for them.

### R16 — preserve independent Tool-test APIs

This task MUST NOT remove or repurpose:

```text
POST /api/studio/preview/tool-tests
GET  /api/studio/preview/tool-tests/:runId
POST /api/studio/preview/tool-tests/:runId/cancel
ToolTestBodySchema.fixtureId
ToolTestBodySchema.externalResponseFixture
```

Those are not the Test Conversations composition UI and remain required by Tool Authoring / Code Response until separately proven obsolete.

### R17 — no mutation outside Preview conversation state

Selecting Features and starting a Test Conversation MUST NOT mutate:

```text
Feature
CommerceFeatureConfiguration
CommerceCapability
CommerceTool
CommerceToolRevision
CommerceRelease
CommerceReleasePointer
CommerceAgentConfiguration
CommerceModelCatalogueEntry
CommerceModelAvailability
CommerceAgentPrompt / revisions
Shop
Subscription/Billing
```

Only bounded Preview conversation state may be written by the existing Preview service/store.

## Work Items

- [x] Create `src/studio/test-conversations/contracts.ts` with the exact R1 browser-safe contracts and continue the C001 Test Conversations module.
- [x] Project Feature data to R2 without Feature Behaviour/edit metadata crossing to the client.
- [x] Load only the validated selected Shop from `resolveStudioShopSelection`.
- [x] Resolve/project effective active Model + ARCH-023 instruction provenance per R4.
- [x] Replace the human conversation-start schema/client input with R5.
- [x] Revalidate `shopId` server-side, resolve the complete effective model/instruction state, and atomically persist the exact R7 `PreviewConversationSnapshot`.
- [x] Refactor the C004 frozen-snapshot schema into the R7 reusable base/refinement without changing its existing validation semantics.
- [x] Add `tests/test-conversation-snapshot.test.ts` covering atomic authored-snapshot creation and stability.
- [x] Implement deterministic Feature checkbox/order/limit semantics.
- [x] Implement the exact Agent configuration / Features / Conversation layout.
- [x] Implement deterministic Start eligibility.
- [x] Add synchronous same-tick Start single-flight gating.
- [x] Preserve original payload/ID for uncertain start reconciliation.
- [x] Lock authoring controls after successful Start and implement local `Start new conversation` reset.
- [x] Keep message execution disabled pending C006/C007; do not route the new UI through synthetic conversation execution.
- [x] Prove no trusted texts/definitions/secrets leak into browser props.
- [x] Prove legacy Preview controls stay absent.
- [x] Prove Tool-test APIs remain unchanged.
- [x] Update focused tests and Completion Report.

## Interfaces / Contracts

Consumes:

```text
ARCH-024-COMMERCE-004
  PreviewSelection = { kind: 'FEATURES'; featureIds: string[] }
  Feature-composed manifest/Tool-definition/Feature-Behaviour composition fragment

ARCH-024-COMMERCE-002 directly
  one effective active Model for the selected Shop
  SHOP -> PRICING_PLAN -> PLATFORM provenance

ARCH-024-COMMERCE-003 is not consumed by this task; it is a separate Studio control-plane ownership cutover.

ARCH-023-COMMERCE-003
  EffectiveAgentConfiguration.instructions.platform
  EffectiveAgentConfiguration.instructions.shop
```

Produces browser start request:

```ts
{
  previewConversationId: string;
  shopId: string;
  selection: {
    kind: 'FEATURES';
    featureIds: string[];
  };
}
```

Produces browser-safe page configuration:

```ts
TestConversationConfigurationState
TestConversationFeatureOption[]
```

Produces the single server-side authored-state contract consumed by C006/C007:

```ts
PreviewConversationSnapshot
  = PreviewFrozenSnapshot
    + shop
    + model
    + instructions
```

No new cross-repository runtime contract is introduced.

## Dependencies

- `ARCH-024-COMMERCE-002`
- `ARCH-024-COMMERCE-004`
- `ARCH-023-COMMERCE-003`

All must be `complete` before this task becomes executable. C002 supplies effective model/provenance resolution, C004 supplies Feature/Capability/Tool composition, and ARCH-023-COMMERCE-003 supplies the accepted Platform + optional Shop Instruction provenance captured by the authored snapshot.

## Enables

- `ARCH-024-COMMERCE-006`

## Acceptance Criteria

- [x] Test Conversations shows only the replacement Agent configuration / Features / Conversation workflow.
- [x] No raw/unvalidated URL `shopId` reaches the conversation start path.
- [x] No Shop selected => Start disabled with the exact R9 guidance.
- [x] Broken/unavailable effective Agent Configuration => Start disabled with a bounded message.
- [x] READY configuration displays the exact effective Model and Platform/Shop Instruction revision provenance.
- [x] Platform/Shop Instruction text itself is not sent to the browser by this screen.
- [x] Model configuration JSON is not sent to the browser by this screen.
- [x] Feature Behaviour text is not sent to the browser by this screen.
- [x] Every Feature with Capabilities has exactly one checkbox.
- [x] Zero-Capability Features are visible but not selectable.
- [x] Inactive Features remain selectable and are labelled `Inactive · testable`.
- [x] Disabled Capability/Tool status is informational and does not remove it from explicit Feature composition.
- [x] Selection order follows user checkbox selection order exactly.
- [x] Re-selecting a Feature appends it to the end of `featureIds`.
- [x] The client prevents more than 32 selected Features.
- [x] Start request is exactly `{ previewConversationId, shopId, selection: { kind:'FEATURES', featureIds } }`.
- [x] Conversation creation revalidates the Shop server-side.
- [x] Stored Feature-composed grant uses the exact validated Shop ID, not `preview-<admin>`.
- [x] C005 is the only task that assembles the complete authored Conversation Configuration Snapshot; it contains exact Shop id/domain, model/provenance/configuration, Platform/optional Shop instruction revisions+text and the C004 composition fragment.
- [x] Refactoring `PreviewFrozenSnapshotSchema` into a reusable base/refinement preserves every existing C004 size/content validation for both narrow and complete snapshots.
- [x] The complete snapshot contains no OpenRouter, Shopify or External HTTP credential material.
- [x] Later model/instruction/Feature/Tool authoring edits do not alter an already-started conversation; a new conversation resolves current authored state.
- [x] Shopify-session absence alone does not prevent Start.
- [x] Same-tick repeated Start activations dispatch exactly one request and one conversation ID.
- [x] Unknown Start outcome can only reconcile with the exact original ID/shop/Feature payload.
- [x] Successful Start locks Feature selection until `Start new conversation`.
- [x] New UI does not submit message runs in this task and does not silently use the old synthetic conversation runtime.
- [x] Tool-test fixture APIs remain intact.
- [x] Legacy Preview selectors/labels listed in R15 are absent.
- [x] No authoring/business rows are mutated by Feature selection/conversation creation.

## Validation

Before running Node commands:

```bash
command -v node >/dev/null 2>&1 || \
  source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"
```

Then inspect `moda-interact-commerce/package.json` and use the repository-declared scripts rather than assuming command names.

Required validation:

- [x] Focused `test-conversations-screen.test.tsx` coverage for R8-R13 and R15.
- [x] Focused `preview-page.test.tsx` or equivalent coverage for R2-R4/R14.
- [x] Focused `test-conversations-client.test.ts` coverage for exact selected-Shop start payload and uncertain same-ID handling.
- [x] Focused `preview-routes.test.ts` coverage proving strict R5 body parsing and rejection of legacy fields.
- [x] Focused `preview-service.test.ts` coverage proving server-side Shop validation and exact grant Shop identity.
- [x] Focused `test-conversation-snapshot.test.ts` coverage proving R7 atomic snapshot creation, exact provenance, stability after later authoring edits, new-conversation refresh, and absence of operational secrets.
- [x] Existing Tool-test/Code Response Preview tests remain green, proving R16.
- [x] Targeted ESLint for every changed Commerce source/test file.
- [x] Changed-file TypeScript diagnostics are zero.
- [x] Repository typecheck command required by the current Commerce package/task baseline, with any unrelated known baseline recorded by baseline ID rather than silently ignored.
- [x] Production build if declared/required by the Commerce repository baseline for changed Next.js page/client code.
- [x] `git diff --check`.

No live Shopify/OpenRouter call is required by this task.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect`, and STOP.

Do not begin ARCH-024-COMMERCE-006 or any follow-on task.

## Implementation Notes

- Prefer extending the accepted Preview conversation service/store seams rather than creating a second Test Conversation store.
- **Conversation Configuration Snapshot ownership is final in this task.** Extend C004's existing `selection + bundle.manifest + snapshot.definitions + snapshot.prompts` composition fragment exactly once with `snapshot.shop`, `snapshot.model` and `snapshot.instructions`. Do not create a second parallel persisted snapshot object.
- This task intentionally keeps message execution disabled so the new product UI cannot misrepresent the retained synthetic runtime as real selected-Shop/OpenRouter execution.
- C006 and C007 consume `PreviewConversationSnapshot` unchanged. C006 owns live selected-Shop Tool execution; C007 owns live OpenRouter credential resolution/model invocation. Neither task may add authored snapshot fields.

## Completion Report

### Status

Ready for Architect review after Attempt 2 evidence-only rework. Implementation commits `9f395d1aca723c5ffe99bdae0c4fcbc929aec664` and `7bf981db210de46ccda3d66fd21c0d194944b062` contain the C005 implementation. Attempt 2 made no implementation-source changes.

### Files Changed

- `app/preview/page.tsx` — loads validated Shop, projects browser-safe Feature data, and resolves effective model/instruction provenance.
- `components/studio-screen.tsx` — replaces the obsolete synthetic Preview description with the required Test Conversations description.
- `src/commerce/integration/preview/adapters.ts` — revalidates the exact Shop, resolves effective configuration, and builds the selected-Shop composition/snapshot inputs.
- `src/commerce/preview/redis-store.ts` — decodes persisted conversations with the required complete authored snapshot schema.
- `src/commerce/preview/service.ts` — validates complete server-owned snapshot provenance before claiming a conversation and reads trusted instruction text from that snapshot.
- `src/commerce/preview/types.ts` — adds the strict selected-Shop start body and complete snapshot schemas while retaining the independent Tool-test contract.
- `src/studio/test-conversations/client.ts` — sends the exact selected-Shop request and classifies uncertain outcomes.
- `src/studio/test-conversations/contracts.ts` — defines the bounded browser-safe Feature/configuration/request types.
- `src/studio/test-conversations/test-conversations-screen.tsx` — implements Feature selection, configuration display, start/reconcile/reset and disabled runtime controls.
- `tests/external-preview.test.ts` — replaces obsolete conversation-scoped external fixture execution expectations with strict selected-Shop request rejection coverage; standalone Tool-test/Code Response fixture processing remains covered.
- `tests/feature-preview-composition.test.ts` — adapts C004 composition coverage to the accepted Shop/effective-configuration reads.
- `tests/preview-integration.test.ts` — verifies selected-Shop and effective provenance adapter integration.
- `tests/preview-page.test.tsx` — verifies page projection and browser-data boundaries.
- `tests/preview-redis-lua.test.ts` — migrates persistence fixtures to the complete snapshot.
- `tests/preview-routes.test.ts` — verifies exact start-body parsing and retained Tool-test routes.
- `tests/preview-service.test.ts` — migrates selected-Shop fixtures and preserves applicable lifecycle/Tool-test regressions; removes legacy mode/prompt-loader cases whose selectors are no longer part of the contract.
- `tests/preview-store.test.ts` — migrates stored conversation fixtures to the complete snapshot.
- `tests/test-conversation-snapshot.test.ts` — verifies atomic snapshot provenance, replay stability, refresh, fail-closed validation and no operational secrets.
- `tests/test-conversations-client.test.ts` — verifies the exact request body and uncertain/error handling.
- `tests/test-conversations-screen.test.tsx` — covers selection semantics, same-tick single-flight, uncertainty reconciliation, success lock/reset and legacy-control absence.

### Work Completed

- Implemented the Feature-only Test Conversations surface and browser-safe selected-Shop start client contract.
- The page uses only `resolveStudioShopSelection(...).selectedShop`, projects exact Feature/Capability/Tool display fields, resolves effective configuration, and sends no trusted instruction text or model configuration to the browser.
- The server revalidates the requested Shop, composes the ordered Feature IDs, validates effective model/instruction provenance, uses the exact validated Shop ID in the grant, and validates the complete immutable snapshot before persistence.
- Added snapshot schemas for Shop identity, model provenance/configuration and Platform/optional Shop instruction revisions/text; retained the narrower composition schema for independent Tool-test state.
- Implemented deterministic selection ordering/limits, disabled no-Capability Features, informational inactive/disabled states, synchronous duplicate protection, same-payload uncertain reconciliation, post-success lock/reset, and the required disabled message controls.
- Preserved independent Tool-test APIs and standalone external fixture/Code Response processing. Removed only conversation-scoped synthetic external fixture runtime expectations superseded by the exact C005 selected-Shop body. No database, Shared, Admin, Background, Gateway, C006 or C007 implementation was changed.

### Validation Results

- Focused Preview/UI/snapshot/adapter test run: 10 files passed, 63 tests passed. After the final UI wording adjustment, the directly affected screen/adapter run passed 2 files, 12 tests.
- Focused retained external fixture/Tool-test and Code Response processor run: 3 files passed, 28 tests passed; final `external-preview.test.ts` run passed 16/16.
- Tool-test route/service regressions passed within the focused Preview test run.
- `npm run typecheck` passed, including Next.js route type generation and `tsc --noEmit`.
- `npm run build` passed, including manuals/code-runtime packaging and smoke checks, Prisma generation, and Next.js production build. Build emitted the existing Nunjucks dynamic-require warnings.
- Targeted ESLint across all changed Commerce source/test files passed without warnings; `git diff --check` passed.
- Full Commerce Vitest suite after the test migration: 160 files, 136 passed, 19 failed, 5 skipped; 1,312 tests passed, 29 failed, 9 skipped. The focused C005 and retained Tool-test/Code Response suites pass, but no accepted baseline ID was available to classify the remaining full-suite failures.
- Implementation commits `9f395d1aca723c5ffe99bdae0c4fcbc929aec664` and `7bf981db210de46ccda3d66fd21c0d194944b062` are published to the mirrored implementation task branch. The database submodule remains at `cfeeb12456b4e05067a96857a8c47837d7e33bbd` and was not changed.

### Deviations

No product-scope deviation. Legacy conversation tests tied to the removed FIXTURE/MODEL selector or the superseded Prompt-loader start path were removed or migrated; independent Tool-test contracts and applicable run lifecycle coverage remain.

### Assumptions

The full-suite failures require Architect triage because no accepted baseline identifier or failure attribution was available during this task attempt.

### Unresolved Issues

The full Commerce Vitest suite is not green (19 failing files / 29 failing tests). Focused C005 and retained Tool-test/Code Response coverage is green; the remaining broader failures were not modified or represented as an accepted baseline.

### Architectural Concerns

None. Message execution remains disabled for C006/C007, and the complete authored snapshot is persisted once without live operational credentials.

### Attempt 2 — Full-suite baseline comparison and prepared-execution evidence

#### Prepared execution

```text
canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent task worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-024-COMMERCE-005
parent branch: task/ARCH-024-COMMERCE-005
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-024-COMMERCE-005
implementation branch: task/ARCH-024-COMMERCE-005
shared/default workspace checkout used for task edits: no
shared implementation checkout used for task edits: no
another task worktree reused: no

parent remote task synchronization at preparation: not-needed
parent origin/main incorporated at preparation: yes
implementation remote task synchronization at preparation: not-needed
implementation origin/main incorporated at preparation: yes
parent preparation head: a555444c8c3dd1a963329cba58824c5f7ec003ed
implementation prepared head: 4a38f092d3a360e19c0bae8432961109cdd78917

dependency gate: passed
  ARCH-024-COMMERCE-002: complete
  ARCH-024-COMMERCE-004: complete
  ARCH-023-COMMERCE-003: complete
git submodule sync --recursive: passed
git submodule update --init --recursive: passed
recursive implementation submodule: database at cfeeb12456b4e05067a96857a8c47837d7e33bbd (initialized)

Attempt 2 claim: executor copilot; claimed_at 2026-10-01T22:26:21Z
claim transition: ready / attempt 1 -> in_progress / attempt 2
durable claim commit: 228902dcc41ce6ea2d8f55f6f849050a429879bb (committed and pushed)
final parent preparation sync: remote task fast-forward not-needed; origin/main already-current
```

#### Paired full-suite comparison

The same `npx vitest run` command was executed on the synchronized pre-task Commerce commit `1318596b523190a8c422cf0fb9ddfeae06847e63` and prepared C005 implementation head `4a38f092d3a360e19c0bae8432961109cdd78917`. Both runs used Node `v24.19.0`, npm `11.17.0`, Vitest `5.0.1`, the same installed dependency tree/package-lock, database submodule `cfeeb12456b4e05067a96857a8c47837d7e33bbd`, and the same local integration-test environment.

```text
Baseline 1318596b523190a8c422cf0fb9ddfeae06847e63:
  157 files: 23 failed, 129 passed, 5 skipped
  1,348 tests: 60 failed, 1,279 passed, 9 skipped

Submitted 4a38f092d3a360e19c0bae8432961109cdd78917:
  160 files: 19 failed, 136 passed, 5 skipped
  1,363 tests: 29 failed, 1,325 passed, 9 skipped

Failure comparison:
  28 individual failed test identifiers are common to both runs.
  Five collection/setup failures are common to both runs.
  32 individual failures occur only on the baseline.
  One individual failure occurs only on the submitted run; it is an unrelated
  Shopify Admin UI timeout and passes when run alone (1 passed, 42 skipped).
```

Common individual failing test identifiers:

- `tests/admin-explorer.test.tsx`: `builds and validates a representable selection before merging query fields into an existing draft`; `cancel returns to the validated origin without merging temporary Explorer state`; `keeps Validate available when the visual candidate cannot yet be built and reports the blocking reason`; `keeps exact raw text for an unchanged literal mapping and drops stale buffers`; `offers a return action beside validation without applying temporary Explorer state`; `preserves a valid manual query that is not representable and returns it unchanged`; `round-trips a newly visual-authored string literal through the New Tool Request editor`; `shows validation progress while the Shopify Admin validation request is in flight`; `validates Request query while preserving malformed unrelated editor buffers`; `validates a restored visual selection even when the selected root field is outside the loaded schema page`.
- `tests/agent-configuration-retained-read.test.ts`: `tracks model and prompt CAS versions on one retained row across clear operations`.
- `tests/agent-contract-validation.test.ts`: `rejects unknown scalar paths and non-list items paths`.
- `tests/auth-entrypoints.test.ts`: `keeps NextAuth and health public while the MCP route remains private`.
- `tests/backend-postgres-rehearsal.test.ts`: `publishes once, replays durably, rejects stale CAS, races across connections, and rolls back injected failure`.
- `tests/discount-evaluator.test.ts`: `retains preview purpose, environment, and trace correlation in eligibility telemetry`.
- `tests/discovery-limits.test.ts`: `allows 60 sequential requests and rejects the 61st in the rolling window`.
- `tests/health.test.ts`: `bounds hanging dependencies under two seconds and aborts Redis`; `readiness checks required dependencies and has no release-publication dependency`.
- `tests/merchant-knowledge-embedding.test.ts`: `validates the exact OpenAI provenance environment contract`.
- `tests/policy-operation-authoring-server-actions.test.ts`: `returns UNAVAILABLE for invalid or unregistered operation identities without fallback`.
- `tests/policy-operation-result-template.test.ts`: `reports whether each currently registered operation result is template-compatible`.
- `tests/preview-model-provider.test.ts`: `defaults disabled without provider settings and validates both providers`.
- `tests/studio-workspace.test.tsx`: `authors a reusable tool without publishing and navigates to its returned ID`; `exposes the failure class when a named Studio action rejects unexpectedly`; `keeps newer edits dirty when an earlier save completes`; `resets editor state when a mounted detail changes to another record`; `retains editor input after stale CAS`; `retains incremental invalid JSON and saves only the complete canonical tool definition`.

Common collection/setup failure identifiers:

- `tests/agent-configuration-model-postgres.test.ts` (0 tests collected).
- `tests/agent-configuration-prompts-postgres.test.ts` (0 tests collected).
- `tests/c20-integration-fixture.test.ts` (0 tests collected).
- `tests/local-external-mcp-diagnostic.test.ts` (0 tests collected).
- `tests/studio-integration-c20.test.ts` (0 tests collected).

Baseline-only failing test identifiers:

- `tests/code-request-processor.test.ts`: `does not expose network or host capabilities`; `rejects unsafe args, oversized input, missing entrypoints, and cancellation`; `rejects unsafe output through the Commerce descriptor schema`; `rejects unsafe request output values through the processor`; `returns a deterministic canonical descriptor`.
- `tests/code-response-processor.test.ts`: `keeps simultaneous inputs isolated`; `leaves result-schema enforcement at the Shared validation boundary`; `maps syntax, deadline, cancellation, and output-limit failures`; `rejects malformed responses and non-object output roots`; `runs v2 with Moda helpers and keeps unsupported versions unavailable`; `transforms JSON through the accepted kernel`; `transforms TEXT without attempting JSON parsing`.
- `tests/code-runtime-proof.test.ts`: `cancels and cleans up workers`; `compiles valid code and rejects syntax without running it`; `executes the deterministic text transform with exact output`; `keeps concurrent inputs isolated and throttles the fifth active run`; `keeps expected guest syntax diagnostics out of operational error logs`; `keeps validation intrinsics outside guest mutation`; `proves supervisor termination after a built-in operation starts`; `rejects enumerable and non-enumerable custom serialization hooks`; `rejects forbidden host capabilities and invalid output shapes`; `retains capacity until cancelled workers terminate`; `terminates infinite loops and recovers the process`.
- `tests/external-preview.test.ts`: `rejects a selected non external conversation fixture before persistence`; `rejects foreign conversation fixtures before persistence`; `reuses the same JavaScript fixture processor for tool-test and conversation execution`; `runs JavaScript sample through the accepted code processor and receipt lifecycle`; `runs a frozen conversation external fixture without live provider or credential access`; `uses developmentBypass as the complete authorization signal regardless of role or staff state`; `validates canonical code content hashes and rejects stale source`.
- `tests/external-tool-authoring-validation.test.ts`: `rejects an unsafe JavaScript request descriptor during preview`; `resolves the same explicit structured and literal bindings before real QuickJS preview`.

Submitted-only failing test identifier:

- `tests/shopify-admin-tools-ui.test.tsx`: `saves, publishes through the canonical action, and reopens the exact Policy binding read-only` timed out during the full suite; isolated rerun passed (1 passed, 42 skipped). It is outside C005 ownership and is not represented as baseline-equivalent.

No Test Conversations or Preview test failed in the submitted run. The submitted tree has fewer failed tests/files overall; the only submitted-only failure is the unrelated, non-reproducing isolated timeout above. Therefore the comparison identifies no new or worsened C005-owned failure, and no implementation-source correction was warranted. The full suite is not literally failure-for-failure baseline-equivalent because of that one submitted-only timeout; it is classified here explicitly rather than hidden under an aggregate claim.

#### Final task-branch publication evidence

The implementation task branch was fast-forward-pushed to the launcher-prepared head `4a38f092d3a360e19c0bae8432961109cdd78917`, which contains the remote C005 implementation commits and launcher-incorporated `origin/main`; its remote task ref now equals that head. The implementation worktree is clean and local head equals remote. Before this report commit, the parent worktree was clean at the pushed Attempt 2 claim commit `228902dcc41ce6ea2d8f55f6f849050a429879bb`, matching its remote. This report is the only parent task file change; after it is committed and pushed, the parent worktree will be verified clean with local head equal to its remote task ref.

## Architect Review

### Review Status

Accepted — Attempt 2

### Review Notes

Attempt 2 closes both evidence-only corrections from Attempt 1. No C005-owned implementation source/test file changed during the retry; direct comparison with the previously reviewed C005 submission confirms the Feature-only Test Conversations implementation remains unchanged while the prepared implementation branch incorporates later accepted `origin/main` work.

**A1-R1 — closed: paired full-suite non-regression evidence is sufficient.** The same `npx vitest run` command was executed under the same Node/npm/Vitest/dependency/database-submodule/integration-test environment on synchronized pre-task Commerce commit `1318596b523190a8c422cf0fb9ddfeae06847e63` and submitted prepared head `4a38f092d3a360e19c0bae8432961109cdd78917`. The baseline recorded 23 failing files / 60 failed tests plus five collection failures; the submitted tree recorded 19 failing files / 29 failed tests with the same five collection failures. Twenty-eight failed test identifiers are common, 32 failures are baseline-only, and the sole submitted-only failure is `tests/shopify-admin-tools-ui.test.tsx` / `saves, publishes through the canonical action, and reopens the exact Policy binding read-only`, which is outside C005 ownership and passed in isolated rerun (`1 passed, 42 skipped`). No Test Conversations or Preview test failed in the submitted run. The evidence therefore demonstrates no new or worsened C005-owned regression without incorrectly claiming literal failure-for-failure baseline equivalence.

**A1-R2 — closed: deterministic prepared-execution evidence is durable.** The Completion Report records the canonical workspace root; dedicated parent and Commerce implementation worktrees; matching `task/ARCH-024-COMMERCE-005` branches; no shared/default or prior-task worktree edits; parent/implementation `origin/main` incorporation; dependency gate; recursive submodule sync/materialisation; database gitlink `cfeeb12456b4e05067a96857a8c47837d7e33bbd`; Attempt 2 claim metadata and durable claim commit `228902dcc41ce6ea2d8f55f6f849050a429879bb`; prepared implementation head `4a38f092d3a360e19c0bae8432961109cdd78917`; and final clean, remote-aligned task-branch evidence. The developer handoff identifies final parent report commit `22af5c0b` and confirms both task worktrees are clean and match their remote refs.

The implementation conclusions from Attempt 1 therefore stand. The selected-Shop browser contract is strict and server-revalidated; the browser receives no trusted instruction/model configuration/Feature Behaviour payloads; C005 owns one complete immutable authored snapshot; Feature selection order and limits are deterministic; Start is same-tick single-flight safe; uncertain outcomes replay the exact original identity/payload; successful Start freezes authoring controls; message execution remains disabled for C006/C007; retained Tool-test/Code Response APIs remain separate; and no authoring/business state outside Preview conversation state is mutated.

### Reviewed Files

Implementation/review evidence:

- Attempt 1 C005 submission -> Attempt 2 prepared-head comparison for all C005-owned implementation/test files
- `moda-interact-commerce/app/preview/page.tsx`
- `moda-interact-commerce/components/studio-screen.tsx`
- `moda-interact-commerce/src/commerce/integration/preview/adapters.ts`
- `moda-interact-commerce/src/commerce/preview/redis-store.ts`
- `moda-interact-commerce/src/commerce/preview/service.ts`
- `moda-interact-commerce/src/commerce/preview/types.ts`
- `moda-interact-commerce/src/studio/test-conversations/client.ts`
- `moda-interact-commerce/src/studio/test-conversations/contracts.ts`
- `moda-interact-commerce/src/studio/test-conversations/test-conversations-screen.tsx`
- focused C005 Preview/UI/snapshot/adapter tests
- retained Tool-test / Code Response tests
- Attempt 2 paired full-suite failure-identifier evidence

Parent coordination:

- `docs/decisions/commerce/ARCH-024/COMMERCE-005-build-feature-composed-test-conversations-ui.md`
- `docs/decisions/commerce/ARCH-024/COMMERCE-006-execute-test-conversation-tools-against-selected-shop.md`
- `docs/decisions/commerce/ARCH-024/_index.md`
- `docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`
- `docs/architecture/_index.md`

### Validation Reviewed

- Submitted required/focused validation remains green: 63 focused C005 tests and 28 retained Tool-test/Code Response tests, targeted ESLint, `npm run typecheck`, production build and `git diff --check`.
- Paired full-suite comparison: synchronized baseline `1318596b523190a8c422cf0fb9ddfeae06847e63` = 23 failing files / 60 failed tests; submitted `4a38f092d3a360e19c0bae8432961109cdd78917` = 19 failing files / 29 failed tests; 28 failed test identifiers plus five collection failures common; 32 baseline-only; one unrelated submitted-only timeout passes in isolation.
- Direct archive comparison confirms C005-owned implementation/test files are unchanged from the previously reviewed submission; Attempt 2 is evidence-only.
- Completion Report records the launcher-resolved physical-isolation, synchronization, recursive-submodule, claim/publication and final clean-worktree evidence required by the architect protocol.
- The uploaded archive contains no installed dependency tree or usable Git metadata, so the reviewer could not independently replay Node commands or query remote refs; acceptance relies on direct source/report inspection plus the durable paired-run/launcher evidence.

### Architecture Conformance

Conforms. C005 owns only the selected-Shop Feature-composed Test Conversations authoring/start boundary and complete authored Conversation Configuration Snapshot. Real selected-Shop Tool execution remains C006; OpenRouter conversation execution remains C007. Repository ownership, trusted-data boundaries, snapshot immutability, Tool-test separation and no-business-mutation constraints are preserved.

### Follow-up

`ARCH-024-COMMERCE-006` becomes Ready because its sole dependency, C005, is now Complete. Do not start C007 until C006 is architect-accepted Complete. No follow-on task is claimed or started by this review.
