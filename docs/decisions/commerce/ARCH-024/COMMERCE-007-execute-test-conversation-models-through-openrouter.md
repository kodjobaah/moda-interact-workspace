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
status: review
priority: 50
executor: copilot
claimed_at: 2026-10-02T09:21:33Z
attempt: 2
depends_on:
  - ARCH-024-COMMERCE-006
  - ARCH-024-SHARED-002
enables:
  - ARCH-024-GATEWAY-001
created: 2026-09-30
updated: 2026-10-02
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

Consume the exact authored model configuration plus ARCH-023 Platform/optional Shop Instructions already frozen by ARCH-024-COMMERCE-005 in the server-side `PreviewConversationSnapshot`. During every model invocation, resolve and decrypt the **current** OpenRouter credential for the current Commerce environment and supply it explicitly to the Shared OpenRouter runtime.

The target model path is:

```text
conversation.snapshot
        |
        +-- shop id/domain
        +-- exact active model + provenance/configuration
        +-- Platform Instructions
        +-- optional Shop Instructions
        +-- Feature/Capability/Tool/Behaviour composition
        |
        v
immutable authored Conversation Configuration Snapshot
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
- COMMERCE-004 creates the Feature composition fragment; COMMERCE-005 is the single owner that atomically creates the complete selected-Shop `PreviewConversationSnapshot` including Shop, model and instruction state.
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

src/studio/test-conversations/test-conversations-screen.tsx
src/studio/test-conversations/client.ts

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
tests/test-conversations-client.test.ts
tests/test-conversations-screen.test.tsx
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

### R2 — consume the exact C005 PreviewConversationSnapshot; do not extend authored state

ARCH-024-COMMERCE-005 already defines and stores the complete authored snapshot:

```ts
PreviewConversationSnapshot =
  PreviewFrozenSnapshot
  + snapshot.shop
  + snapshot.model
  + snapshot.instructions
```

This task MUST import/use the accepted local `PreviewConversationSnapshot` / `PreviewConversationSnapshotSchema` implementation. It MUST NOT add model/instruction/Shop fields to the snapshot, create a second persisted snapshot, or move authored state to separate `StoredConversation` fields.

The retained fixture-backed Tool-test boundary MAY continue using the narrower `PreviewFrozenSnapshot` where required.

Do not persist anywhere in Preview state:

```text
OpenRouter credential
credential ciphertext
credential nonce
credential authTag
credential keyId
Shopify access token
External HTTP credential
```

### R3 — never re-resolve authored model/instructions after Start Conversation

The C005 browser configuration summary remains display-only, and C005 server Start already resolved and validated the authoritative model/instruction snapshot.

For every conversation run, C007 MUST use only:

```text
conversation.snapshot.model
conversation.snapshot.instructions
conversation.snapshot.shop
conversation.bundle.manifest
conversation.snapshot.definitions
conversation.snapshot.prompts
```

C007 MUST NOT call `resolveEffectiveConfiguration(...)`, `getEffectiveAgentConfiguration(...)`, current prompt-template reads, or current Model Catalogue reads to replace authored state for an already-started conversation.

A new conversation is the only path that resolves newer model/instruction authored configuration.

Before invoking the model, parse/validate `conversation.snapshot` through the accepted `PreviewConversationSnapshotSchema`. Invalid/missing authored state is bounded `UNAVAILABLE`/`INCOMPATIBLE_VERSION` and MUST occur before OpenRouter invocation.

### R4 — Conversation Configuration Snapshot semantics are mandatory

After Start Conversation commits, subsequent messages MUST use only:

```text
conversation.snapshot.model
conversation.snapshot.instructions
conversation.bundle.manifest
conversation.snapshot.definitions
conversation.snapshot.prompts
conversation.snapshot.shop
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
6. obtain the exact canonical AAD string from the published Shared contract and UTF-8 encode it before `decipher.setAAD(...)`:

```ts
createCommerceOpenRouterCredentialAad({
  environment,
  keyId: row.keyId,
})
```

7. require the decrypted secret to be 1..8192 UTF-8 bytes and contain no `\r`, `\n` or `\0`;
8. return the exact decrypted string;
9. map missing row, missing key, malformed envelope, authentication failure, database failure or invalid plaintext to one bounded `UNAVAILABLE` error without leaking detail.

Use the published Shared `createCommerceOpenRouterCredentialAad(...)` contract for the exact AAD string. ARCH-024-ADMIN-003 and BACKGROUND-001 independently use the same Shared contract; this task MUST NOT consume Admin implementation source or invent provider-specific credential formats.

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
turn.shopId          = conversation.snapshot.shop.id
turn.conversationId  = conversation.id
checkoutRecoveryId   = preview-<conversation.id>
```

`checkoutRecoveryId` is an execution identity only; do not create a durable CheckoutRecovery row.

Do not use `fixture.context` for the human conversation. Use only bounded server-owned preview context such as:

```ts
{
  shop: {
    id: conversation.snapshot.shop.id,
    domain: conversation.snapshot.shop.domain,
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

1. C007 accepts the exact C005 `PreviewConversationSnapshot` and does not call the effective-model/instruction resolver during a conversation run.
2. Model factory receives exact frozen `snapshot.model.provider/providerModelId/configuration`.
3. Platform + optional Shop Instructions come only from `snapshot.instructions` for an existing conversation.
4. Changing current Agent Configuration or current Instruction revisions after Start does not affect the next run because C007 never rereads them.
5. Feature Behaviour still comes from the frozen manifest and is not reread.
6. Credential resolver is called before **every** model invocation.
7. Replacing credential A with B between model invocations causes the second client construction to receive B.
8. Removing the credential causes the next invocation to fail bounded `UNAVAILABLE`.
9. Cancellation signal reaches the credential/model path.
10. Preview host safety + frozen Platform + optional Shop instructions reach `ModelRequest.instructions` in the required order relative to runner-owned instructions.
11. real selected-Shop C006 Tool executor remains the only human conversation Tool path.
12. no fixture context/model is used by the human conversation.
13. provider/model/API key environment variables are not consulted.
14. provider errors do not expose secret/raw provider response detail.
15. missing/invalid `PreviewConversationSnapshot` fails before OpenRouter/credential-provider side effects.

C005 owns the separate Start/snapshot-creation regression matrix; do not duplicate that ownership in C007.

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
5. seal credential `credential-A` using the exact published Shared `createCommerceOpenRouterCredentialAad(...)` contract;
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

- [x] Update Commerce to the exact SHARED-002 published package version (`@modainteract/moda-interact-shared@1.1.0`).
- [x] Remove the bespoke Preview HTTP model provider and obsolete provider tests.
- [x] Consume and validate the exact C005 `PreviewConversationSnapshot`; do not extend authored state in C007.
- [x] Prove model/instructions/Shop are never re-resolved for an already-started conversation.
- [x] Implement the AES-256-GCM current-environment OpenRouter credential resolver using the shared Commerce keyring.
- [x] Refactor generic credential-keyring parsing only as required for reuse; preserve External Connection behaviour.
- [x] Implement per-invocation current-credential OpenRouter model construction through Shared `OpenRouterModelClient`.
- [x] Remove human conversation FIXTURE/MODEL mode state and scripted fixture model execution.
- [x] Make model-run quota unconditional for human conversation runs in both stores.
- [x] Wire exact host instruction order and selected-Shop context into `runCommerceTurn`.
- [x] Pass the existing Commerce `StructuredLogger` child (`purpose=preview`, `previewRunId`) into `runCommerceTurn`; do not create a second logger.
- [x] Reduce Commerce Preview config to `COMMERCE_PREVIEW_ENABLED` only.
- [x] Enable Test Conversation message Send/reconcile/cancel behaviour with same-tick single-flight protection.
- [x] Add focused runtime tests.
- [x] Add disposable PostgreSQL credential-rotation/decryption proof.
- [x] Preserve independent fixture-backed Tool Authoring / Code Response Tool-test APIs.
- [x] Perform final static cleanup/reference audit.

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
    createCommerceOpenRouterCredentialAad

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
complete PreviewConversationSnapshot from C005:
  snapshot.shop
  snapshot.model
  snapshot.instructions
  frozen Tool definitions / Feature Behaviour
selected-Shop conversation grant
real selected-Shop conversation Tool executor
```

From ARCH-024-DATABASE-001 + the published ARCH-024-SHARED-002 contract:

```text
one encrypted OpenRouter credential row per environment
AES-256-GCM durable envelope columns
canonical Shared OpenRouter credential AAD construction
same Commerce credential keyring
```

ARCH-024-ADMIN-003 independently implements the credential writer/UI against the same published Shared AAD contract; Commerce does not consume Admin implementation source.

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

ADMIN-003 is deliberately not an implementation dependency. Focused/integration validation seeds the accepted `CommerceOpenRouterCredential` database row directly and uses the published Shared AAD contract; Admin owns the independent credential-management control plane.

## Enables

- `ARCH-024-GATEWAY-001`

Later ARCH-024 system-test tasks will also depend on this task when materialised.

## Acceptance Criteria

- [x] Human Test Conversations use the exact effective active Agent model already captured by C005 in `conversation.snapshot.model`.
- [x] Platform + optional Shop Instructions already captured by C005 remain stable for the conversation and are not re-resolved by C007.
- [x] Later Agent Configuration/Instruction edits do not alter an already-started conversation.
- [x] A new conversation observes current Agent Configuration/Instructions.
- [x] Every model invocation resolves the current environment OpenRouter credential from PostgreSQL.
- [x] Replacing the credential takes effect on the next model invocation without Commerce restart or new conversation.
- [x] Removing/misconfiguring the credential fails bounded `UNAVAILABLE` without leaking secret material.
- [x] The decrypted credential is never persisted in Preview state or browser data.
- [x] Commerce uses the published Shared `OpenRouterModelClient`/`runCommerceTurn`; there is no direct LangChain/OpenRouter/LangGraph SDK dependency.
- [x] The existing Commerce `StructuredLogger` is passed into `runCommerceTurn` with safe preview context, and logging failure does not change the run result.
- [x] The old bespoke Preview provider implementation is removed.
- [x] `COMMERCE_PREVIEW_PROVIDER`, `COMMERCE_PREVIEW_MODEL` and `COMMERCE_PREVIEW_API_KEY` are no longer read by Commerce application/runtime code.
- [x] `COMMERCE_PREVIEW_ENABLED` remains the only Preview model-execution kill switch.
- [x] Human conversation FIXTURE/MODEL mode state is removed.
- [x] Human conversation runs always use the existing model quota in memory and Redis.
- [x] Tool-test fixture APIs remain separate and functional.
- [x] `runCommerceTurn` receives host safety, Platform and optional Shop Instructions in deterministic trusted order.
- [x] Human conversation context uses the selected Shop and no synthetic fixture context.
- [x] Test Conversation message composer is enabled only after a conversation starts and has same-tick single-flight protection.
- [x] Unknown run outcomes preserve the original run ID for reconciliation.
- [x] No live OpenRouter call occurs in automated validation.
- [x] Disposable PostgreSQL proof demonstrates hot credential replacement without recreating the resolver/service.

## Validation

Before running Node-related validation:

```bash
command -v node >/dev/null 2>&1 || \
  source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"
```

Inspect the synchronized `package.json` first and use the declared scripts. Required validation for this task:

- [x] Prisma generation succeeds against the integrated ARCH-024 database submodule.
- [x] Focused runtime tests pass (7 files, 57 tests):

```bash
npx vitest run \
  tests/preview-openrouter-runtime.test.ts \
  tests/preview-service.test.ts \
  tests/preview-store.test.ts \
  tests/preview-routes.test.ts \
  tests/test-conversations-client.test.ts \
  tests/test-conversations-screen.test.tsx \
  tests/preview-integration.test.ts
```

- [x] Redis parity/regression test passes (1 file, 9 tests):

```bash
npx vitest run tests/preview-redis-lua.test.ts
```

- [x] Independent Tool-test/Code Response regressions covering `/api/studio/preview/tool-tests` remain green using the repository's current focused suites (16 external-preview tests and 7 Code Response tests).
- [x] Disposable PostgreSQL credential proof passes:

```bash
node scripts/run-preview-openrouter-disposable.mjs
```

- [x] `npm run typecheck` succeeds; no changed-file diagnostic was introduced.
- [x] Targeted ESLint succeeds for every changed TypeScript/TSX/JavaScript file with no warnings or errors on the final pass.
- [x] Production build succeeds:

```bash
npm run build
```

- [x] Static reference audit from R18 passes.
- [x] `git diff --check` passes.
- [x] The disposable PostgreSQL runner removes every task-owned container/network in `finally`.

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

- **Conversation Configuration Snapshot** is owned and fully assembled by C005. C007 consumes it unchanged; it does not include operational credentials.
- Credential lookup on every model invocation is intentional. Do not optimize it into process-lifetime credential caching in this task.
- Reusing `COMMERCE_CONNECTION_KEYS_JSON` is intentional. ARCH-024 does not create a second encryption root merely for OpenRouter.
- The AAD shape in R5 is a Shared-owned cross-repository contract. Admin, Commerce and Background must all consume `createCommerceOpenRouterCredentialAad(...)`; if any implementation conflicts with the published contract, stop and return the architecture issue rather than silently choosing another AAD.
- Commerce-local LangGraph remains out of scope. The published Shared `runCommerceTurn` is LangGraph-backed and remains the canonical orchestration boundary; Commerce does not import or configure LangGraph directly.
- Do not reintroduce an OpenRouter/provider/model selector on Test Conversations. The model is selected in Agent Configuration and captured server-side at Start.

## Completion Report

### Status

Ready for Review

### Files Changed

`.env.example`, `README.md`, `app/preview/page.tsx`, `docs/commerce-preview-integration.md`, `docs/runtime-compatibility.md`, `lib/preview/runtime.ts`, `lib/server/config.ts`, `lib/server/credential-keyring.ts`, `package.json`, `scripts/clean-clone.sh`, `scripts/run-preview-openrouter-disposable.mjs`, `src/commerce/integration/backend.ts`, `src/commerce/integration/preview/adapters.ts`, `src/commerce/integration/preview/model-provider.ts` (deleted), `src/commerce/integration/preview/model-runtime.ts`, `src/commerce/integration/preview/openrouter-credential.ts`, `src/commerce/preview/redis-store.ts`, `src/commerce/preview/service.ts`, `src/commerce/preview/store.ts`, `src/commerce/preview/types.ts`, `src/studio/test-conversations/client.ts`, `src/studio/test-conversations/test-conversations-screen.tsx`, `tests/external-preview.test.ts`, `tests/preview-integration.test.ts`, `tests/preview-model-provider.test.ts` (deleted), `tests/preview-openrouter-postgres.test.ts`, `tests/preview-openrouter-runtime.test.ts`, `tests/preview-redis-lua.test.ts`, `tests/preview-routes.test.ts`, `tests/preview-service.test.ts`, `tests/preview-store.test.ts`, `tests/test-conversations-screen.test.tsx`.

### Work Completed

Replaced the human Test Conversation fixture/provider split with the published Shared runtime and exact C005 snapshot; implemented the environment-scoped encrypted credential resolver and per-invocation credential refresh; reused the existing Commerce keyring; retained isolated fixture Tool-test APIs and unconditional conversation quotas; enabled composer/send/reconcile/cancel flows; added frozen-snapshot, logger-failure, runtime and PostgreSQL credential-rotation regressions. The Shared dependency remains pinned to the exact accepted `@modainteract/moda-interact-shared@1.1.0`; no Shared or database schema changes were made. The generic keyring helper and retained fixture adapter domain correction are the only mechanically related additional implementation files. No automated test called OpenRouter.

### Validation Results

All required validation passed on attempt 2:

- `node scripts/run-preview-openrouter-disposable.mjs` — integrated migrations and the PostgreSQL credential rotation/decryption proof passed (1 test); cleanup verified zero owned containers or networks remain. No OpenRouter call was made.
- Focused browser regression `npx vitest run tests/test-conversations-screen.test.tsx` — 1 file, 13 tests passed.
- Required seven-file focused Vitest suite — 7 files, 57 tests passed.
- `npx vitest run tests/preview-redis-lua.test.ts` — 1 file, 9 tests passed.
- `npm run code-runtime:package`, `npm run test:arch020-external-preview`, and `npm run test:arch020-code-processor` — package step passed; suites passed with 16 and 7 tests respectively.
- `npx prisma generate --schema database/prisma/schema.prisma` — Prisma Client v6.19.3 generated. `npm run build` also completed its declared Prisma generation step successfully.
- `npm run typecheck` — passed.
- Targeted ESLint on both attempt-2 changed TSX files — passed with no warnings or errors.
- `npm run build` — passed. Existing Nunjucks `node-loaders.js` dynamic-dependency warnings appeared in two traces.
- R18 static audit — passed: no forbidden provider/mode/hostname/direct-SDK references in application/runtime source; `/api/studio/preview/tool-tests` exists and the retained fixture Tool-test executor remains referenced.
- `git diff --check` — passed.

### Deviations

No scope or contract deviation. The stale `preview.myshopify.com` literal in the retained fixture adapter was changed to `fixture.invalid` to satisfy R18. A no-op legacy-selector test input was removed because spreading an empty object left the valid request unchanged.

### Assumptions

The accepted Shared release remains `1.1.0`, and the integrated database submodule already contains the accepted ARCH-024 schema/migrations; both were verified in the task worktree. The disposable proof is local-only and uses no provider credentials.

### Unresolved Issues

None identified. The production build retains the noted Nunjucks dynamic-dependency warnings; the build succeeds and the warnings are outside the changed runtime path.

### Architectural Concerns

None.

### Architect Review Corrections

- **A1-R1 — implemented.** Cancel dispatches for the retained conversation/run identity while the original run is pending, gates repeated cancellation, and lets cancel/reconcile races settle only that operation. Known terminal outcomes release it once; UNKNOWN retains it. Changed `src/studio/test-conversations/test-conversations-screen.tsx` and `tests/test-conversations-screen.test.tsx`. The focused 13-test browser suite and seven-file suite passed.
- **A1-R2 — implemented.** Start new conversation is disabled while a run is pending or UNKNOWN, its handler also refuses to clear an unresolved run, and stale asynchronous results are fenced by the retained operation identity. Regressions cover pending/UNKNOWN lockout and late results after a subsequent conversation. Changed the same two files; the focused 13-test browser suite and seven-file suite passed.
- **A1-R3 — implemented (evidence only).** This Completion Report records the prepared paths, branch/start synchronization, dependency gate, database gitlink, both claim attempts and claim commit IDs, plus final implementation publication. No implementation source changes were made for this item. The parent report commit and matching remote head are published on the task branch; their exact final SHA is included in the task handoff because a commit cannot contain its own hash.

### Prepared Attempt and Publication Evidence

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Dedicated parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-024-COMMERCE-007`, branch `task/ARCH-024-COMMERCE-007`.
- Dedicated Commerce implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-024-COMMERCE-007`, branch `task/ARCH-024-COMMERCE-007`.
- The shared/default checkout and any previous task worktree were not used for implementation or parent task edits.
- Attempt 2 prepared start: parent HEAD `f9a15f1b8bdb24e88901eab02592a705898d60c4`; implementation HEAD `20b037095bde85a446236a42e4192fb3ad67644a`. For both repositories, task-branch remote fast-forward was not needed and `origin/main` was already incorporated/current. Recursive submodule sync/update passed during preparation; the integrated database gitlink is `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.
- Dependency gate passed: `ARCH-024-COMMERCE-006` and `ARCH-024-SHARED-002` were Complete.
- Attempt 1 claim metadata from parent history: executor `copilot`, claimed at `2026-10-02T07:46:08Z`, attempt `1`; durable claim commit `cd4ef983c823e7b1abc3b444adc10568b27ad078`. The attempt-1 Changes Requested review is commit `55089c6007302c79ee895fd144e86ba91b3a9581`.
- Attempt 2 claim metadata: executor `copilot`, claimed at `2026-10-02T09:21:33Z`, attempt `2`; durable parent claim commit `bb9df450128b3c45d98fb9bd3f675f7b2785c89e`.
- Final implementation commit and remote task-branch head: `c3a7fe7ff4414fa8c731361dbc171f52f39bb59d`; local and `origin/task/ARCH-024-COMMERCE-007` matched, and the implementation worktree was clean.
- Parent Completion Report publication commit and remote task-branch head: `a264d9d1cd1b20a4be4de843a544c5a0bf4962a3`; local and `origin/task/ARCH-024-COMMERCE-007` matched, and the parent worktree was clean at verification. This evidence-only follow-up updates the report without changing the implementation commit or task status.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 review found the server/runtime architecture broadly conformant, including frozen C005 snapshot use, per-invocation OpenRouter credential resolution, Shared `OpenRouterModelClient`/`runCommerceTurn` reuse, selected-Shop C006 Tool execution, unconditional human-conversation model quotas, independent fixture Tool-test retention, bounded provider failures and no live provider validation.

Three bounded corrections are required before acceptance.

**A1-R1 — the visible Cancel run action is unreachable while a run is actually pending.**

`sendMessage()` sets `runInFlightRef.current = true` before the POST and keeps it true while `reconcileRun(...)` polls a `RUNNING` run to terminal state. The UI renders `Cancel run` when `runPending` is true, but `cancelPendingRun()` immediately returns when `runInFlightRef.current` is true. Therefore the normal pending-run state exposes a Cancel button that cannot dispatch `cancelTestConversationRun(...)`.

Correct the client-side run lifecycle so:

- Send remains same-tick single-flight safe and cannot allocate a second run ID while the original run is unresolved;
- Cancel can be invoked for the exact retained `{ conversationId, previewRunId }` while that run is `RUNNING`;
- repeated same-tick Cancel activation is bounded/idempotently gated;
- cancel/reconcile races settle only the retained original run and do not create a new run ID;
- known `CANCELLED`, `FAILED` or `COMPLETED` results release the local pending gate exactly once;
- `UNKNOWN` retains the original operation for explicit reconciliation.

Add focused browser regression coverage that starts a run returning `RUNNING`, proves the rendered Cancel button calls the cancel client with the exact original conversation/run IDs, and proves the terminal cancellation/reconciliation result is settled without a second Start Run request.

**A1-R2 — Start new conversation may orphan or cross-contaminate an unresolved run.**

`Start new conversation` remains enabled while `runPending` or `runUnknown`. `startNewConversation()` clears `pendingRunRef` and `runInFlightRef` even though the original server run may still be active or require reconciliation. The earlier asynchronous send/poll can then settle after local state has been reset (or after another conversation has started), appending the old run transcript/status into the wrong local conversation and discarding the exact operation needed for `UNKNOWN` reconciliation.

Preserve the C007 exact-run reconciliation invariant. At minimum:

- do not allow local conversation reset/new-conversation transition while a run is pending or `UNKNOWN`;
- defensively fence `startNewConversation()` against an unresolved `pendingRunRef`;
- do not clear the retained original run identity until a known terminal result has been settled;
- add focused regressions proving a pending or `UNKNOWN` run cannot be abandoned through `Start new conversation`, and an old asynchronous result cannot populate a later conversation.

A different implementation is acceptable if it proves the same lifecycle isolation without weakening same-tick/idempotency behaviour.

**A1-R3 — mandatory deterministic execution evidence is absent from the Completion Report.**

The task report records validation results and final implementation/report commit summaries but does not durably record the launcher-resolved prepared execution packet required by the repository-task review protocol. Attempt 2 must record the actual evidence for:

- canonical `workspace_root`;
- dedicated parent task worktree and exact `task/ARCH-024-COMMERCE-007` branch;
- dedicated Commerce implementation worktree and exact matching task branch;
- confirmation that the shared/default checkout and a previous task worktree were not used;
- parent task-branch synchronization and `origin/main` incorporation at attempt start;
- implementation task-branch synchronization and `origin/main` incorporation at attempt start;
- dependency gate showing `ARCH-024-COMMERCE-006` and `ARCH-024-SHARED-002` Complete;
- recursive submodule sync/update and the exact integrated database gitlink identity;
- Attempt 1/Attempt 2 claim metadata and durable claim commit(s);
- final implementation commit and remote task-branch head;
- final parent report commit and remote task-branch head;
- clean final status and local-head-equals-remote-head evidence for both worktrees.

A1-R3 is evidence-only and must not cause source churn. If the launcher packet is available, copy the actual prepared evidence rather than reconstructing paths or synchronization claims from memory.

No Database, Shared, Admin, Background or Gateway implementation change is requested. Do not start `ARCH-024-GATEWAY-001`.

### Reviewed Files

- `src/studio/test-conversations/test-conversations-screen.tsx`
- `src/studio/test-conversations/client.ts`
- `src/commerce/preview/service.ts`
- `src/commerce/preview/store.ts`
- `src/commerce/preview/redis-store.ts`
- `src/commerce/integration/preview/model-runtime.ts`
- `src/commerce/integration/preview/openrouter-credential.ts`
- `lib/preview/runtime.ts`
- `lib/server/config.ts`
- `lib/server/credential-keyring.ts`
- `tests/test-conversations-screen.test.tsx`
- `tests/preview-openrouter-runtime.test.ts`
- `tests/preview-openrouter-postgres.test.ts`
- `tests/preview-service.test.ts`
- `tests/preview-redis-lua.test.ts`
- `docs/decisions/commerce/ARCH-024/COMMERCE-007-execute-test-conversation-models-through-openrouter.md`

### Validation Reviewed

- Submitted: required seven-file focused runtime suite — 54 tests passed.
- Submitted: Redis parity suite — 9 tests passed.
- Submitted: retained Tool-test/Code Response regressions — 16 + 7 tests passed.
- Submitted: disposable PostgreSQL credential-rotation/decryption proof passed with cleanup.
- Submitted: Prisma generation, targeted ESLint, typecheck, production build, R18 static audit and `git diff --check` passed.
- Direct source review confirmed no live Commerce runtime reference to the removed bespoke Preview provider/mode variables and no direct Commerce LangChain/OpenRouter/LangGraph import.
- Direct source review confirmed the current Cancel handler is fenced by the same long-lived `runInFlightRef` used by Send/polling and therefore cannot dispatch during the visible pending state.
- Direct source review confirmed `Start new conversation` is not disabled for pending/UNKNOWN runs and clears the retained pending-run identity.
- The uploaded review archive does not contain installed `node_modules` or usable Git metadata, so dependency-backed commands and remote-head identity were not independently replayed in the architect environment.

### Architecture Conformance

Changes Requested. The server-side frozen-snapshot/OpenRouter runtime, credential rotation semantics, selected-Shop Tool execution boundary, quota/storage split and provider cleanup conform. The browser run lifecycle does not yet satisfy C007 cancellation and exact unresolved-run reconciliation requirements, and the Completion Report lacks mandatory physical-isolation/start-of-attempt evidence.

### Follow-up

Return the same task through the normal `/moda-task ARCH-024-COMMERCE-007` path. The next authorized claim becomes Attempt 2. Correct A1-R1/A1-R2, add the focused UI lifecycle regressions, rerun the complete C007 validation contract, add the A1-R3 prepared-execution evidence, set the task back to `review`, and STOP. `ARCH-024-GATEWAY-001` remains dependency-gated until C007 is architect-accepted Complete.
