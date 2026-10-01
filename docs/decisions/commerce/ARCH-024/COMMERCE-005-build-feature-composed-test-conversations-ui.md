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
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
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

- [ ] Create `src/studio/test-conversations/contracts.ts` with the exact R1 browser-safe contracts and continue the C001 Test Conversations module.
- [ ] Project Feature data to R2 without Feature Behaviour/edit metadata crossing to the client.
- [ ] Load only the validated selected Shop from `resolveStudioShopSelection`.
- [ ] Resolve/project effective active Model + ARCH-023 instruction provenance per R4.
- [ ] Replace the human conversation-start schema/client input with R5.
- [ ] Revalidate `shopId` server-side, resolve the complete effective model/instruction state, and atomically persist the exact R7 `PreviewConversationSnapshot`.
- [ ] Refactor the C004 frozen-snapshot schema into the R7 reusable base/refinement without changing its existing validation semantics.
- [ ] Add `tests/test-conversation-snapshot.test.ts` covering atomic authored-snapshot creation and stability.
- [ ] Implement deterministic Feature checkbox/order/limit semantics.
- [ ] Implement the exact Agent configuration / Features / Conversation layout.
- [ ] Implement deterministic Start eligibility.
- [ ] Add synchronous same-tick Start single-flight gating.
- [ ] Preserve original payload/ID for uncertain start reconciliation.
- [ ] Lock authoring controls after successful Start and implement local `Start new conversation` reset.
- [ ] Keep message execution disabled pending C006/C007; do not route the new UI through synthetic conversation execution.
- [ ] Prove no trusted texts/definitions/secrets leak into browser props.
- [ ] Prove legacy Preview controls stay absent.
- [ ] Prove Tool-test APIs remain unchanged.
- [ ] Update focused tests and Completion Report.

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

- [ ] Test Conversations shows only the replacement Agent configuration / Features / Conversation workflow.
- [ ] No raw/unvalidated URL `shopId` reaches the conversation start path.
- [ ] No Shop selected => Start disabled with the exact R9 guidance.
- [ ] Broken/unavailable effective Agent Configuration => Start disabled with a bounded message.
- [ ] READY configuration displays the exact effective Model and Platform/Shop Instruction revision provenance.
- [ ] Platform/Shop Instruction text itself is not sent to the browser by this screen.
- [ ] Model configuration JSON is not sent to the browser by this screen.
- [ ] Feature Behaviour text is not sent to the browser by this screen.
- [ ] Every Feature with Capabilities has exactly one checkbox.
- [ ] Zero-Capability Features are visible but not selectable.
- [ ] Inactive Features remain selectable and are labelled `Inactive · testable`.
- [ ] Disabled Capability/Tool status is informational and does not remove it from explicit Feature composition.
- [ ] Selection order follows user checkbox selection order exactly.
- [ ] Re-selecting a Feature appends it to the end of `featureIds`.
- [ ] The client prevents more than 32 selected Features.
- [ ] Start request is exactly `{ previewConversationId, shopId, selection: { kind:'FEATURES', featureIds } }`.
- [ ] Conversation creation revalidates the Shop server-side.
- [ ] Stored Feature-composed grant uses the exact validated Shop ID, not `preview-<admin>`.
- [ ] C005 is the only task that assembles the complete authored Conversation Configuration Snapshot; it contains exact Shop id/domain, model/provenance/configuration, Platform/optional Shop instruction revisions+text and the C004 composition fragment.
- [ ] Refactoring `PreviewFrozenSnapshotSchema` into a reusable base/refinement preserves every existing C004 size/content validation for both narrow and complete snapshots.
- [ ] The complete snapshot contains no OpenRouter, Shopify or External HTTP credential material.
- [ ] Later model/instruction/Feature/Tool authoring edits do not alter an already-started conversation; a new conversation resolves current authored state.
- [ ] Shopify-session absence alone does not prevent Start.
- [ ] Same-tick repeated Start activations dispatch exactly one request and one conversation ID.
- [ ] Unknown Start outcome can only reconcile with the exact original ID/shop/Feature payload.
- [ ] Successful Start locks Feature selection until `Start new conversation`.
- [ ] New UI does not submit message runs in this task and does not silently use the old synthetic conversation runtime.
- [ ] Tool-test fixture APIs remain intact.
- [ ] Legacy Preview selectors/labels listed in R15 are absent.
- [ ] No authoring/business rows are mutated by Feature selection/conversation creation.

## Validation

Before running Node commands:

```bash
command -v node >/dev/null 2>&1 || \
  source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"
```

Then inspect `moda-interact-commerce/package.json` and use the repository-declared scripts rather than assuming command names.

Required validation:

- [ ] Focused `test-conversations-screen.test.tsx` coverage for R8-R13 and R15.
- [ ] Focused `preview-page.test.tsx` or equivalent coverage for R2-R4/R14.
- [ ] Focused `test-conversations-client.test.ts` coverage for exact selected-Shop start payload and uncertain same-ID handling.
- [ ] Focused `preview-routes.test.ts` coverage proving strict R5 body parsing and rejection of legacy fields.
- [ ] Focused `preview-service.test.ts` coverage proving server-side Shop validation and exact grant Shop identity.
- [ ] Focused `test-conversation-snapshot.test.ts` coverage proving R7 atomic snapshot creation, exact provenance, stability after later authoring edits, new-conversation refresh, and absence of operational secrets.
- [ ] Existing Tool-test/Code Response Preview tests remain green, proving R16.
- [ ] Targeted ESLint for every changed Commerce source/test file.
- [ ] Changed-file TypeScript diagnostics are zero.
- [ ] Repository typecheck command required by the current Commerce package/task baseline, with any unrelated known baseline recorded by baseline ID rather than silently ignored.
- [ ] Production build if declared/required by the Commerce repository baseline for changed Next.js page/client code.
- [ ] `git diff --check`.

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

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

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

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
