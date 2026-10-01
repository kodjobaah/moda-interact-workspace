---
id: ARCH-024-COMMERCE-007
architecture_id: ARCH-024
title: Execute Test Conversation models through OpenRouter
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
  - ARCH-024-COMMERCE-006
  - ARCH-024-SHARED-002
  - ARCH-024-ADMIN-003
enables: []
created: 2026-09-30
updated: 2026-10-01
---

# Execute Test Conversation models through OpenRouter

## Architecture

Architecture ID:

`ARCH-024`

Architecture document:

`docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`

Coordinator:

`moda_architect`

## Objective

Complete the ARCH-024 human Test Conversation runtime by replacing the retained static/synthetic Preview model provider with the **single effective active model** selected through Agent Configuration and the published Shared `OpenRouterModelClient`.

At Test Conversation start, capture the exact authored model configuration plus ARCH-023 Platform/optional Shop Instructions into the existing server-side Conversation Configuration Snapshot. During every model invocation, resolve and decrypt the **current** OpenRouter credential for the current Commerce environment and supply it explicitly to the Shared OpenRouter runtime.

The target model path is:

```text
validated selected Shop
        |
        v
resolveEffectiveConfiguration(...)
        |
        +-- exact active model
        |     provider
        |     providerModelId
        |     configurationSchemaVersion
        |     configuration
        |
        +-- Platform Instructions
        +-- optional Shop Instructions
        |
        v
Conversation Configuration Snapshot
        |
        | every model invocation
        v
read current CommerceOpenRouterCredential(environment)
        |
        v
decrypt with Commerce credential keyring
        |
        v
OpenRouterModelClient
        |
        v
LangChain ChatOpenRouter
        |
        v
OpenRouter
```

The authored model/instruction configuration is stable for one Test Conversation. Operational secrets are not stable conversation state: credential replacement must affect the next model invocation without restarting Commerce and without starting a new conversation.

This task is the final Commerce task in the initial ARCH-024 Test Conversation sequence. It also enables the message composer that ARCH-024-COMMERCE-005 deliberately leaves disabled.

## Context

The integrated pre-ARCH-024 Preview runtime has a bespoke provider implementation:

```text
src/commerce/integration/preview/model-provider.ts
```

with static configuration:

```text
COMMERCE_PREVIEW_PROVIDER
COMMERCE_PREVIEW_MODEL
COMMERCE_PREVIEW_API_KEY
```

and a conversation mode switch between a scripted fixture model and the HTTP provider model.

ARCH-024 changes that architecture before this task executes:

- DATABASE-001 persists dynamic `provider + providerModelId`, bounded model `configuration`, Availability and one encrypted `CommerceOpenRouterCredential` per environment.
- SHARED-001 defines the model contracts/OpenRouter client and implements/instruments the modular LangGraph runner; SHARED-002 publishes the combined accepted package implementing the existing `CommerceModelInvoker` / `ModelRequest` / `ModelStep` runner boundary.
- COMMERCE-002 resolves exactly one effective active model for the selected Shop.
- COMMERCE-004/005 create a Feature-composed Test Conversation and selected-Shop Conversation Configuration Snapshot boundary.
- COMMERCE-006 installs real selected-Shop Tool execution while deliberately leaving human model turns disabled.
- ARCH-023-COMMERCE-003, already a dependency of the accepted C005 chain, supplies additive trusted Platform + optional Shop Instructions.
- ADMIN-003 owns set/replace/remove of the encrypted OpenRouter credential and uses the same sealed-secret contract defined below.

ARCH-024 is pre-production for this Preview runtime. Existing development Preview Redis records using the old `FIXTURE` / `MODEL` conversation-mode shape do not require backwards compatibility and may expire/be cleared.

## Scope

Primary implementation surface:

```text
package.json
package-lock.json

lib/server/config.ts
lib/server/connections.ts
lib/preview/runtime.ts

src/commerce/preview/types.ts
src/commerce/preview/service.ts
src/commerce/preview/store.ts
src/commerce/preview/redis-store.ts

src/commerce/integration/preview/adapters.ts
src/commerce/integration/preview/model-provider.ts        DELETE when unreferenced
src/commerce/integration/preview/openrouter-credential.ts CREATE
src/commerce/integration/preview/model-runtime.ts         CREATE

src/studio/preview/preview-screen.tsx
src/studio/preview/client.ts

app/api/studio/preview/conversations/[id]/runs/route.ts
app/api/studio/preview/conversations/[id]/runs/[runId]/route.ts
app/api/studio/preview/conversations/[id]/runs/[runId]/cancel/route.ts

tests/preview-model-provider.test.ts                      DELETE when unreferenced
tests/preview-openrouter-runtime.test.ts                  CREATE
tests/preview-openrouter-postgres.test.ts                 CREATE
tests/preview-service.test.ts
tests/preview-store.test.ts
tests/preview-redis-lua.test.ts
tests/preview-routes.test.ts
tests/preview-client.test.ts
tests/preview-screen.test.tsx
tests/preview-integration.test.ts

scripts/run-preview-openrouter-disposable.mjs             CREATE
```

If an accepted C001-C006 implementation has moved/renamed an equivalent Preview file, modify that accepted equivalent instead of creating compatibility aliases. Record every such substitution in the Completion Report.

Additional Commerce files may be changed only when mechanically required to consume the exact SHARED-002 package or to reuse the existing credential keyring parser. Name and justify each additional file in the Completion Report.

## Out of Scope

- Model Catalogue creation/editing.
- Model Availability creation/editing.
- Active model selection UI; COMMERCE-003 owns that.
- OpenRouter credential mutation UI or encryption commands; ADMIN-003 owns them.
- Database schema/migration changes.
- Shared contract/runtime changes.
- Background/production CommerceAgent OpenRouter adoption.
- Gateway/Render environment-variable removal; GATEWAY-001 owns deployment cleanup.
- Commerce-local LangGraph/agent orchestration. The published Shared `runCommerceTurn` owns the ARCH-024 LangGraph graph; Commerce MUST NOT add a direct `@langchain/langgraph` dependency or local graph.
- New model-provider SDKs in `moda-interact-commerce`.
- Direct `@langchain/openrouter` or `@langchain/core` imports in Commerce.
- Model fallback lists.
- Merchant-facing model selection.
- Capability selection/exclusion.
- Re-resolving current Feature/Capability/Tool authoring on every message.
- Storing OpenRouter, Shopify or External HTTP credentials in Preview Redis state.
- Reintroducing Fixture Scenario, Model Mode, Release/Draft or other removed human Preview controls.
- Changing independent fixture-backed `/api/studio/preview/tool-tests` behaviour.

## Requirements

### R1 — consume exactly the published ARCH-024 Shared runtime

After ARCH-024-SHARED-002 is architect-accepted, read its Completion Report and update:

```text
@modainteract/moda-interact-shared
```

to the **exact published version** recorded there.

Do not use:

```text
workspace:
file:
link:
Git URL
unpublished Shared task-branch source
```

Commerce MUST import:

```ts
import type { CommerceModelInvoker } from '@modainteract/moda-interact-shared/commerce/runner';
import {
  CommerceModelConfigurationSchema,
  CommerceModelProviderSchema,
  CommerceProviderModelIdSchema,
  CommerceModelSelectionSourceSchema,
} from '@modainteract/moda-interact-shared/commerce/model';
import {
  OpenRouterModelClient,
  type OpenRouterModelClientOptions,
} from '@modainteract/moda-interact-shared/commerce/model/node';
```

Do not add direct `@langchain/openrouter` or `@langchain/core` dependencies to `moda-interact-commerce`.

Delete the old bespoke provider file once all references are removed:

```text
src/commerce/integration/preview/model-provider.ts
```

and delete its obsolete direct-HTTP provider tests:

```text
tests/preview-model-provider.test.ts
```

Static validation MUST prove Commerce has no direct LangChain/OpenRouter/LangGraph package import outside the published Shared package imports above.

### R2 — extend the existing Preview snapshot; do not create a second persisted conversation snapshot

Keep the C004/C005 authored snapshot as the single server-side Conversation Configuration Snapshot.

In `src/commerce/preview/types.ts`, add strict schemas/types equivalent to:

```ts
export const PreviewConversationModelSnapshotSchema = z.strictObject({
  selectionSource: CommerceModelSelectionSourceSchema,
  merchantPricingPlanId: SavedIdSchema.nullable(),
  shopifyPlanHandle: z.string().trim().min(1).max(255).nullable(),
  catalogueEntryId: SavedIdSchema,
  provider: CommerceModelProviderSchema,
  providerModelId: CommerceProviderModelIdSchema,
  configurationSchemaVersion: z.number().int().positive(),
  configuration: CommerceModelConfigurationSchema,
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
```

Create a conversation-specific extension of the existing authored snapshot rather than a parallel top-level object:

```ts
export const PreviewConversationSnapshotSchema =
  PreviewFrozenSnapshotSchema.extend({
    model: PreviewConversationModelSnapshotSchema,
    instructions: PreviewConversationInstructionsSnapshotSchema,
  });
```

`StoredConversation.snapshot` for the human Feature Test Conversation MUST use `PreviewConversationSnapshot`.

The retained fixture-backed Tool-test boundary MAY continue using the narrower `PreviewFrozenSnapshot` where required. Do not force Tool-test fixtures to have model/instruction state.

Do not persist in either snapshot:

```text
OpenRouter credential
credential ciphertext
credential nonce
credential authTag
credential keyId
Shopify access token
External HTTP credential
```

### R3 — resolve and capture the exact model/instructions only when Start Conversation commits

Add one server-only Preview adapter/factory in the accepted Preview integration surface. It MUST resolve the selected Shop's effective Agent Configuration using the accepted:

```ts
resolveEffectiveConfiguration(...)
```

inside the server start path after the selected Shop has been revalidated by C005.

The browser's configuration summary is display-only and MUST NOT be accepted as trusted model/instruction input.

Start succeeds only when:

```text
effective model source = PLATFORM, PRICING_PLAN or SHOP
effective model.model != null
Platform Instructions are present and valid
Shop Instructions are either absent or valid
```

Map the model snapshot exactly from the effective model result:

```text
selectionSource              -> model.selectionSource
merchantPricingPlanId        -> model.merchantPricingPlanId
shopifyPlanHandle            -> model.shopifyPlanHandle
catalogueEntryId             -> model.model.catalogueEntryId
provider                     -> model.model.provider
providerModelId              -> model.model.providerModelId
configurationSchemaVersion   -> model.model.configurationSchemaVersion
configuration                -> model.model.configuration
```

Validate `provider`, `providerModelId` and `configuration` again through the published Shared schemas before storing. Enforce snapshot provenance exactly:

```text
selectionSource = PRICING_PLAN
    -> merchantPricingPlanId and shopifyPlanHandle are non-null

selectionSource = PLATFORM or SHOP
    -> merchantPricingPlanId and shopifyPlanHandle are null
```

Map instructions exactly from ARCH-023 additive effective instructions:

```text
platform.revisionId      -> instructions.platform.revision.id
platform.revisionNumber  -> instructions.platform.revision.revisionNumber
platform.text            -> instructions.platform.revision.promptText

shop = null
    when effective instructions.shop = null

otherwise:
shop.revisionId          -> instructions.shop.revision.id
shop.revisionNumber      -> instructions.shop.revision.revisionNumber
shop.text                -> instructions.shop.revision.promptText
```

If the accepted ARCH-023 effective contract names those already-resolved revision fields differently, map the exact accepted equivalents; do not reread current prompt templates or source templates.

Any unavailable/invalid effective configuration MUST fail Start with bounded Preview `UNAVAILABLE` and MUST NOT claim/store a conversation.

### R4 — Conversation Configuration Snapshot semantics are mandatory

After Start Conversation commits, subsequent messages MUST use only:

```text
conversation.snapshot.model
conversation.snapshot.instructions
conversation.bundle.manifest
conversation.snapshot.definitions
conversation.snapshot.prompts
conversation.shop
```

for authored/test configuration.

Subsequent messages MUST NOT reread current:

```text
CommerceAgentConfiguration.modelId
CommerceModelCatalogueEntry configuration
Platform Instructions pointer/revision
Shop Instructions pointer/revision
Feature Behaviour
Capability membership
published Tool revision
```

for that already-started conversation.

Required semantics:

```text
Conversation A starts with Model A / Platform rev 3 / Shop rev 2
Admin changes active model to Model B and publishes Platform rev 4
Conversation A next turn -> still Model A / Platform rev 3 / Shop rev 2
New Conversation B      -> resolves Model B / Platform rev 4 / current Shop Instructions
```

This stability rule applies to authored configuration only. R6 deliberately keeps the credential live.

### R5 — add one exact OpenRouter credential resolver

Create:

```text
src/commerce/integration/preview/openrouter-credential.ts
```

with one exported server-only factory/interface equivalent to:

```ts
export type OpenRouterCredentialResolver = {
  resolve(input: {
    environment: CommerceEnvironment;
    signal: AbortSignal;
  }): Promise<string>;
};

export function createOpenRouterCredentialResolver(input: {
  db: PrismaClient;
  keyring: Readonly<Record<string, Uint8Array>>;
}): OpenRouterCredentialResolver;
```

`resolve(...)` MUST:

1. fail immediately when `signal.aborted`;
2. query exactly one row by:

```text
CommerceOpenRouterCredential.environment = environment
```

3. require the row to exist;
4. require `keyring[row.keyId]` to exist and contain exactly 32 bytes;
5. decrypt with AES-256-GCM using the stored 12-byte nonce and 16-byte auth tag;
6. use this exact UTF-8 AAD payload:

```ts
canonicalJson({
  credentialType: 'OPENROUTER',
  environment,
  keyId: row.keyId,
})
```

7. require the decrypted secret to be 1..8192 UTF-8 bytes and contain no `\r`, `\n` or `\0`;
8. return the exact decrypted string;
9. map missing row, missing key, malformed envelope, authentication failure, database failure or invalid plaintext to one bounded `UNAVAILABLE` error without leaking detail.

ARCH-024-ADMIN-003 MUST use the exact same AES-256-GCM/AAD contract when sealing credentials. This task consumes that accepted contract; do not invent provider-specific credential formats.

Do not cache the decrypted secret.

### R6 — reuse the existing Commerce credential keyring; do not add an OpenRouter API-key environment variable

The OpenRouter credential MUST use the same architecture-approved keyring already used for encrypted Commerce External Connection credentials:

```text
COMMERCE_CONNECTION_KEYS_JSON
```

Do not introduce:

```text
OPENROUTER_API_KEY
COMMERCE_OPENROUTER_API_KEY
COMMERCE_PREVIEW_API_KEY replacement
another encryption keyring
```

If current keyring parsing is embedded inside `createProductionBackendConfig()`, extract only the generic read/validation part into one reusable server-only helper, for example:

```text
lib/server/credential-keyring.ts
```

The helper MUST:

```text
parse COMMERCE_CONNECTION_KEYS_JSON as object<string, base64>
require every decoded key to be exactly 32 bytes
return Readonly<Record<string, Uint8Array>>
never log raw environment/key values
```

External Connection behaviour must remain unchanged after the refactor.

C007 needs only the keyring for decryption. It MUST NOT require `COMMERCE_CONNECTION_ACTIVE_KEY_ID` or `COMMERCE_CONNECTION_COMMAND_HMAC_KEY` merely to invoke OpenRouter.

### R7 — create one model invoker that resolves the current credential on every invocation

Create:

```text
src/commerce/integration/preview/model-runtime.ts
```

Export one factory equivalent to:

```ts
export type PreviewOpenRouterModelFactory =
  (options: OpenRouterModelClientOptions) => CommerceModelInvoker;

export function createPreviewOpenRouterModelInvoker(input: {
  model: PreviewConversationModelSnapshot;
  environment: CommerceEnvironment;
  credentialResolver: OpenRouterCredentialResolver;
  createClient?: PreviewOpenRouterModelFactory;
}): CommerceModelInvoker;
```

Production `createClient` MUST be:

```ts
(options) => new OpenRouterModelClient(options)
```

On **every** `invoke(request, signal)`:

1. require the signal not already aborted;
2. call `credentialResolver.resolve({ environment, signal })`;
3. construct a new `OpenRouterModelClient` using the conversation snapshot's exact:

```text
provider
providerModelId
configurationSchemaVersion
configuration
```

plus the just-resolved credential;
4. invoke it with the exact `ModelRequest` and signal;
5. return the resulting `ModelStep` unchanged.

Do not cache:

```text
credential
OpenRouterModelClient instance
resolved credential row
```

across model invocations.

This is the required live-rotation semantic:

```text
model invocation 1 -> credential A
Admin replaces credential A with B
model invocation 2 -> credential B
```

No service restart and no new Test Conversation are required.

The injectable `createClient` seam is test-only/internal. Do not export it through a browser/client contract.

### R8 — remove the human conversation fixture/model mode split

By the end of C007, every human Feature Test Conversation uses the OpenRouter model runtime.

Remove residual human-conversation mode state from:

```text
StoredConversation
StoredConversationSchema
StoredRun
StoredRunSchema
InMemoryPreviewStateStore
RedisPreviewStateStore / Preview Lua state
PreviewService conversation execution
```

Specifically remove:

```ts
mode: 'FIXTURE' | 'MODEL'
```

from human conversation/run state if still present after accepted C001-C006 work.

Delete `ScriptedFixtureModel` and the conversation `fixtureModel`/`model` selection branch when unreferenced.

Do NOT remove fixture-backed independent Tool-test state or APIs.

Because every human conversation run is now a model run, preserve the existing model-run safety quotas **unconditionally for conversation runs**:

```text
maximum model starts per admin per 60-minute window = 10
maximum concurrent conversation model run per admin  = 1
maximum concurrent conversation model runs globally = 2
model slot lifetime                                  = 120 seconds
```

Tool tests do not consume these model quotas.

The in-memory and Redis implementations MUST implement identical quota semantics.

No compatibility migration for old development Redis state is required.

### R9 — run the Shared Commerce runner with exact trusted instruction ordering

For a human Test Conversation run, create the model invoker from R7 using `conversation.snapshot.model`.

Call `runCommerceTurn(...)` with `hostInstructions` exactly:

```ts
[
  'This is an isolated staff Test Conversation. Never send customer messages or perform mutations.',
  conversation.snapshot.instructions.platform.text,
  ...(conversation.snapshot.instructions.shop
    ? [conversation.snapshot.instructions.shop.text]
    : []),
]
```

Do not concatenate these strings into one string before passing them to the runner.

The resulting authoritative ordering is therefore:

```text
Shared immutable runner kernel
Preview host safety instruction
ARCH-023 Platform Instructions
ARCH-023 Shop Instructions, when present
response-contract instruction
Feature Behaviours from frozen manifest
```

Do not add Tool results, Merchant Knowledge, External HTTP responses, customer messages or provider output to `hostInstructions`.

Use the selected-Shop identity established by C005/C006:

```text
turn.shopId          = conversation.shop.id
turn.conversationId  = conversation.id
checkoutRecoveryId   = preview-<conversation.id>
```

`checkoutRecoveryId` is an execution identity only; do not create a durable CheckoutRecovery row.

Do not use `fixture.context` for the human conversation. Use only bounded server-owned preview context such as:

```ts
{
  shop: {
    id: conversation.shop.id,
    domain: conversation.shop.domain,
  },
  telemetry: {
    environment: this.environment,
    purpose: 'preview',
  },
}
```

Continue using the retained conversation history and C006 `conversationToolExecutor`.

Preserve the current bounded runner budgets unless an accepted earlier ARCH-024 task has already narrowed them:

```text
modelSteps   = 4
remoteCalls  = 4
deadlineMs   = 30,000
outputTokens = 400
```

Do not raise those budgets in this task.

### R9A — pass the existing Commerce StructuredLogger into the Shared runner

`PreviewService` already owns a canonical `StructuredLogger`. When invoking `runCommerceTurn`, pass a child of that existing logger:

```ts
dependencies: {
  model,
  tools,
  now: this.now,
  digest,
  logger: this.logger.child({
    purpose: "preview",
    previewRunId: run.id,
  }),
}
```

Do not create a second logger for the runner. Do not change `service.name=moda-interact-commerce` or the resolved deployment environment.

The host child MUST NOT contain the user message, prompt/instruction text, Tool arguments/results, Merchant Knowledge content, provider body or credentials. Shared adds the `commerce-turn-runner` component and safe turn/grant/release identifiers.

Focused tests must prove Test Conversation runs pass the injected logger and that the same successful/failed result is returned if logging fails.

### R10 — `COMMERCE_PREVIEW_ENABLED` remains the only Commerce Preview model kill switch

In `lib/server/config.ts`, replace the old model/provider Preview configuration with exactly:

```ts
export type PreviewConfig = {
  enabled: boolean;
};
```

Parse only:

```text
COMMERCE_PREVIEW_ENABLED=true|false
```

Remove Commerce application parsing/validation for:

```text
COMMERCE_PREVIEW_PROVIDER
COMMERCE_PREVIEW_MODEL
COMMERCE_PREVIEW_API_KEY
```

Do not add a replacement provider/model/API-key environment variable.

`lib/preview/runtime.ts` MUST wire the database, effective configuration loader, OpenRouter credential resolver and Shared model client from server-owned dependencies.

When `COMMERCE_PREVIEW_ENABLED=false`:

```text
Start Conversation -> bounded UNAVAILABLE
Run Conversation   -> bounded UNAVAILABLE
independent Tool-test APIs -> retain their accepted existing behaviour
```

GATEWAY-001 later removes obsolete deployment declarations; C007 owns only Commerce application/runtime dependence on the old variables.

### R11 — enable the human message composer only after C007 runtime wiring is present

Update the C005 `Conversation` section so the textarea and Send button become usable only when:

```text
conversation has started
Preview runtime is enabled
no run is pending
conversation is not blocked by UNKNOWN outcome
message.trim().length is 1..4000
```

Do not add a Model picker or model-mode selector.

Use the existing conversation run API:

```text
POST /api/studio/preview/conversations/:id/runs
GET  /api/studio/preview/conversations/:id/runs/:runId
POST /api/studio/preview/conversations/:id/runs/:runId/cancel
```

Preserve current run ID/idempotency semantics.

Send MUST be same-tick single-flight safe:

```text
first activation
    -> create one previewRunId
    -> freeze exact message + conversation ID + run ID in an imperative pending ref
    -> dispatch exactly once

second activation in same JS tick
    -> no second ID
    -> no second request
```

For an uncertain run-start/result outcome, retain the original `previewRunId` and reconcile that exact run. Never silently send the message again under a new ID.

On COMPLETED:

```text
append persisted user + assistant transcript returned by/reconciled from server
clear message input
release local pending gate
```

On FAILED/CANCELLED:

```text
show bounded status
release pending gate when outcome is known
```

On UNKNOWN:

```text
lock Send
show the existing bounded reconcile/check-original-run action
```

### R12 — credential rotation must not alter the Conversation Configuration Snapshot

Credential replacement/removal is operational state, not authored model state.

Required behaviour:

```text
Conversation snapshot contains Model A configuration
OpenRouter credential A exists
turn 1 succeeds
Admin replaces credential with B
turn 2 uses B with the same Model A snapshot
Admin removes credential
turn 3 fails bounded UNAVAILABLE
Admin sets credential C
subsequent invocation can use C without Commerce restart or new conversation
```

Never write credential status/version into the conversation snapshot merely to detect rotation.

### R13 — provider/runtime failures are bounded and secret-safe

The public Preview/runner result must never contain:

```text
OpenRouter API key
ciphertext
nonce
authTag
keyId
Authorization header
raw LangChain/OpenRouter exception/body
complete conversation payload
```

Credential read/decrypt/model construction/provider invocation failures must ultimately surface through the existing bounded Preview/runner `UNAVAILABLE` path.

Do not log the decrypted credential or provider response body.

If logging an operational failure, use only bounded identifiers such as:

```text
environment
previewConversationId
previewRunId
catalogueEntryId
provider
providerModelId
```

and the shared structured logger if logging is added.

### R14 — no live OpenRouter call is allowed in repository validation

All automated C007 tests MUST use an injected fake `PreviewOpenRouterModelFactory` / fake `CommerceModelInvoker`.

The tests must prove the exact options passed to the client factory, but MUST NOT call `openrouter.ai` or any external model provider.

No real API credential is required for tests.

### R15 — focused runtime tests are mandatory

Create:

```text
tests/preview-openrouter-runtime.test.ts
```

At minimum prove:

1. Start Conversation captures the exact effective active model identity/configuration.
2. Start captures Platform Instructions and optional Shop Instructions exactly once.
3. Broken/unavailable model prevents conversation creation.
4. Missing/invalid Platform Instructions prevent conversation creation.
5. A later Agent Configuration model change does not change an existing conversation snapshot.
6. A later Platform/Shop Instruction publication does not change an existing conversation snapshot.
7. A new conversation resolves the newer model/instructions.
8. Model factory receives exact frozen provider/providerModelId/configuration.
9. Credential resolver is called before **every** model invocation.
10. Replacing credential A with B between model invocations causes the second client construction to receive B.
11. Removing the credential causes the next invocation to fail bounded `UNAVAILABLE`.
12. Cancellation signal reaches the credential/model path.
13. Preview host safety + Platform + optional Shop instructions reach `ModelRequest.instructions` in the required order relative to runner-owned instructions.
14. Feature Behaviour still comes from the frozen manifest and is not reread.
15. real selected-Shop C006 Tool executor remains the only human conversation Tool path.
16. no fixture context/model is used by the human conversation.
17. provider/model/API key environment variables are not consulted.
18. provider errors do not expose secret/raw provider response detail.

### R16 — real PostgreSQL credential-resolution proof is mandatory

Create:

```text
tests/preview-openrouter-postgres.test.ts
scripts/run-preview-openrouter-disposable.mjs
```

The disposable runner MUST:

1. start a task-owned PostgreSQL container from the repository's accepted PostgreSQL test image;
2. apply the integrated database migrations including ARCH-024-DATABASE-001;
3. create one test PlatformAdmin row required by the credential FK;
4. create a 32-byte in-memory test keyring key;
5. seal credential `credential-A` using the exact ADMIN-003/C007 AES-256-GCM/AAD contract;
6. insert one `CommerceOpenRouterCredential` for `DEVELOPMENT`;
7. resolve and assert exact plaintext `credential-A`;
8. CAS-style replace the row with sealed `credential-B` without recreating the resolver/service;
9. resolve again and assert exact plaintext `credential-B`;
10. delete the row and assert bounded `UNAVAILABLE`;
11. insert a row with an unknown `keyId` and assert bounded `UNAVAILABLE`;
12. insert/tamper ciphertext or auth tag and assert bounded `UNAVAILABLE`;
13. remove the task-owned container/network in `finally`.

Do not print decrypted credentials to stdout/stderr. Assertions compare values only in process memory.

The test MUST NOT call OpenRouter.

### R17 — model-run quota is now unconditional for human conversations

Update both the in-memory and Redis Preview stores so every human conversation run uses the existing model quota:

```text
10 starts / admin / rolling 60 minutes
1 concurrent run / admin
2 concurrent runs globally
120-second slot expiry
```

There is no longer a `conversation.mode === 'MODEL'` condition.

Tests must prove:

```text
all human conversation runs consume quota
Tool-test runs do not consume quota
in-memory and Redis behaviour match
expired slot becomes UNKNOWN and is released exactly as before
```

### R18 — final static cleanup is mandatory

After implementation, static search in `moda-interact-commerce` application/runtime source MUST find no live reference to:

```text
createPreviewModel
PreviewModelProvider
COMMERCE_PREVIEW_PROVIDER
COMMERCE_PREVIEW_MODEL
COMMERCE_PREVIEW_API_KEY
conversation.mode === 'MODEL'
conversation.mode === 'FIXTURE'
ScriptedFixtureModel
preview.myshopify.com
```

Exceptions are allowed only in historical task/document text outside application/runtime source and must be identified in the Completion Report if relevant.

Static search MUST also prove:

```text
no direct @langchain/openrouter import in Commerce
no direct @langchain/core import in Commerce
no direct @langchain/langgraph import in Commerce
/api/studio/preview/tool-tests remains present
retained fixture Tool-test executor remains referenced
```

## Work Items

- [ ] Update Commerce to the exact SHARED-002 published package version.
- [ ] Remove the bespoke Preview HTTP model provider and obsolete provider tests.
- [ ] Extend the existing conversation snapshot with exact model + additive instruction state.
- [ ] Capture effective model/instructions server-side when Start Conversation commits.
- [ ] Implement the AES-256-GCM current-environment OpenRouter credential resolver using the shared Commerce keyring.
- [ ] Refactor generic credential-keyring parsing only as required for reuse; preserve External Connection behaviour.
- [ ] Implement per-invocation current-credential OpenRouter model construction through Shared `OpenRouterModelClient`.
- [ ] Remove human conversation FIXTURE/MODEL mode state and scripted fixture model execution.
- [ ] Make model-run quota unconditional for human conversation runs in both stores.
- [ ] Wire exact host instruction order and selected-Shop context into `runCommerceTurn`.
- [ ] Pass the existing Commerce `StructuredLogger` child (`purpose=preview`, `previewRunId`) into `runCommerceTurn`; do not create a second logger.
- [ ] Reduce Commerce Preview config to `COMMERCE_PREVIEW_ENABLED` only.
- [ ] Enable Test Conversation message Send/reconcile/cancel behaviour with same-tick single-flight protection.
- [ ] Add focused runtime tests.
- [ ] Add disposable PostgreSQL credential-rotation/decryption proof.
- [ ] Preserve independent fixture-backed Tool Authoring / Code Response Tool-test APIs.
- [ ] Perform final static cleanup/reference audit.

## Interfaces / Contracts

### Consumes

From ARCH-024-DATABASE-001:

```text
commerce.CommerceOpenRouterCredential
commerce.CommerceModelCatalogueEntry
commerce.CommerceAgentConfiguration
```

From ARCH-024-SHARED-002:

```text
@modainteract/moda-interact-shared/commerce/model
    CommerceModelConfigurationSchema
    CommerceModelProviderSchema
    CommerceProviderModelIdSchema

@modainteract/moda-interact-shared/commerce/model/node
    OpenRouterModelClient
    OpenRouterModelClientOptions

@modainteract/moda-interact-shared/commerce/runner
    CommerceModelInvoker
    ModelRequest
    ModelStep
    runCommerceTurn
```

From ARCH-024-COMMERCE-002:

```text
one effective active model
ResolvedCommerceModel
selection provenance
```

From ARCH-023-COMMERCE-003:

```text
EffectiveAgentConfiguration.instructions.platform
EffectiveAgentConfiguration.instructions.shop
```

From ARCH-024-COMMERCE-004/005/006:

```text
Feature-composed manifest
frozen Tool definitions / Feature Behaviour
validated selected Shop
selected-Shop conversation grant
real selected-Shop conversation Tool executor
```

From ARCH-024-ADMIN-003:

```text
one encrypted OpenRouter credential per environment
AES-256-GCM sealing contract
same Commerce credential keyring
```

### Produces

A complete human Test Conversation model runtime in which:

```text
conversation authored model/instructions = stable snapshot
OpenRouter credential                   = live per invocation
Tool execution                           = selected-Shop C006 runtime
model execution                          = Shared OpenRouterModelClient
```

No new cross-service queue/event contract is created.

## Dependencies

- `ARCH-024-COMMERCE-006`
- `ARCH-024-SHARED-002`
- `ARCH-024-ADMIN-003`

## Enables

None defined yet. Later ARCH-024 system-test/deployment tasks will depend on this task.

## Acceptance Criteria

- [ ] Human Test Conversations use the effective active Agent model captured at Start Conversation.
- [ ] Platform + optional Shop Instructions are captured at Start and remain stable for the conversation.
- [ ] Later Agent Configuration/Instruction edits do not alter an already-started conversation.
- [ ] A new conversation observes current Agent Configuration/Instructions.
- [ ] Every model invocation resolves the current environment OpenRouter credential from PostgreSQL.
- [ ] Replacing the credential takes effect on the next model invocation without Commerce restart or new conversation.
- [ ] Removing/misconfiguring the credential fails bounded `UNAVAILABLE` without leaking secret material.
- [ ] The decrypted credential is never persisted in Preview state or browser data.
- [ ] Commerce uses the published Shared `OpenRouterModelClient`/`runCommerceTurn`; there is no direct LangChain/OpenRouter/LangGraph SDK dependency.
- [ ] The existing Commerce `StructuredLogger` is passed into `runCommerceTurn` with safe preview context, and logging failure does not change the run result.
- [ ] The old bespoke Preview provider implementation is removed.
- [ ] `COMMERCE_PREVIEW_PROVIDER`, `COMMERCE_PREVIEW_MODEL` and `COMMERCE_PREVIEW_API_KEY` are no longer read by Commerce application/runtime code.
- [ ] `COMMERCE_PREVIEW_ENABLED` remains the only Preview model-execution kill switch.
- [ ] Human conversation FIXTURE/MODEL mode state is removed.
- [ ] Human conversation runs always use the existing model quota in memory and Redis.
- [ ] Tool-test fixture APIs remain separate and functional.
- [ ] `runCommerceTurn` receives host safety, Platform and optional Shop Instructions in deterministic trusted order.
- [ ] Human conversation context uses the selected Shop and no synthetic fixture context.
- [ ] Test Conversation message composer is enabled only after a conversation starts and has same-tick single-flight protection.
- [ ] Unknown run outcomes preserve the original run ID for reconciliation.
- [ ] No live OpenRouter call occurs in automated validation.
- [ ] Disposable PostgreSQL proof demonstrates hot credential replacement without recreating the resolver/service.

## Validation

Before running Node-related validation:

```bash
command -v node >/dev/null 2>&1 || \
  source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"
```

Inspect the synchronized `package.json` first and use the declared scripts. Required validation for this task:

- [ ] Prisma generation succeeds against the integrated ARCH-024 database submodule.
- [ ] Focused runtime tests pass:

```bash
npx vitest run \
  tests/preview-openrouter-runtime.test.ts \
  tests/preview-service.test.ts \
  tests/preview-store.test.ts \
  tests/preview-routes.test.ts \
  tests/preview-client.test.ts \
  tests/preview-screen.test.tsx \
  tests/preview-integration.test.ts
```

- [ ] Redis parity/regression test passes:

```bash
npx vitest run tests/preview-redis-lua.test.ts
```

- [ ] Independent Tool-test/Code Response regressions covering `/api/studio/preview/tool-tests` remain green using the repository's current focused suites.
- [ ] Disposable PostgreSQL credential proof passes:

```bash
node scripts/run-preview-openrouter-disposable.mjs
```

- [ ] `npm run typecheck` succeeds, or any pre-existing baseline diagnostics are recorded exactly according to `docs/development-baseline.md`; no changed-file diagnostic may be introduced.
- [ ] Targeted ESLint succeeds for every changed TypeScript/TSX/JavaScript file.
- [ ] Production build succeeds:

```bash
npm run build
```

- [ ] Static reference audit from R18 passes.
- [ ] `git diff --check` passes.
- [ ] The disposable PostgreSQL runner removes every task-owned container/network in `finally`.

No validation command may send a real request to OpenRouter or any other LLM provider.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

1. complete the Completion Report;
2. set task status to `review`;
3. clear no architect-owned coordination state;
4. return control to `moda_architect`;
5. **STOP**.

Do not begin Background, Gateway or ARCH-024 system-test work.

## Implementation Notes

- **Conversation Configuration Snapshot** means the authored configuration captured once at Start Conversation. It does not include operational credentials.
- Credential lookup on every model invocation is intentional. Do not optimize it into process-lifetime credential caching in this task.
- Reusing `COMMERCE_CONNECTION_KEYS_JSON` is intentional. ARCH-024 does not create a second encryption root merely for OpenRouter.
- The AAD shape in R5 is a cross-repository invariant with ADMIN-003. Any conflict discovered in the accepted Admin implementation is architectural; stop and return it to `moda_architect` rather than silently choosing another AAD.
- Commerce-local LangGraph remains out of scope. The published Shared `runCommerceTurn` is LangGraph-backed and remains the canonical orchestration boundary; Commerce does not import or configure LangGraph directly.
- Do not reintroduce an OpenRouter/provider/model selector on Test Conversations. The model is selected in Agent Configuration and captured server-side at Start.

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
