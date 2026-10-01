---
id: ARCH-024-BACKGROUND-001
architecture_id: ARCH-024
title: Use the effective OpenRouter model for production CommerceAgent turns
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-024-DATABASE-001
  - ARCH-024-SHARED-004
  - ARCH-024-COMMERCE-002
  - ARCH-024-ADMIN-003
enables:
  - ARCH-024-BACKGROUND-002
created: 2026-10-01
updated: 2026-10-01
---

# Use the effective OpenRouter model for production CommerceAgent turns

## Architecture

Architecture ID:

`ARCH-024`

Architecture document:

`docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`

Coordinator:

`moda_architect`

## Objective

Replace the production CommerceAgent's static Groq model selection with the ARCH-024 effective active model and the published Shared OpenRouter runtime, while preserving Background-owned conversation ordering, admission, host execution and MCP Tool flow; the dependent BACKGROUND-002 task removes the redundant one-node Background LangGraph wrapper after Shared owns the actual graph.

For each production CommerceAgent **turn**:

```text
current deployment environment
        +
trusted Shop.id
        ↓
resolve one effective active Commerce model
        ↓
keep that model identity/configuration stable for this turn
        ↓
for every model invocation in the turn:
    resolve current encrypted OpenRouter credential for the environment
    decrypt server-side
    construct Shared OpenRouterModelClient
    invoke existing runCommerceTurn model boundary
```

Operational credential rotation MUST affect the next model invocation without restarting the Background worker. A model-selection change MUST affect the next CommerceAgent turn; it MUST NOT change the model halfway through an already-running turn.

## Context

The integrated Background baseline currently hard-codes production CommerceAgent model execution to Groq:

```text
src/agents/commerce.agent.ts
    -> process.env.GROQ_COMMERCE_MODEL
    -> groq(modelId)

src/providers/groq.provider.ts
    -> process.env.GROQ_API_KEY
    -> @ai-sdk/groq

src/commerce/host.ts
    -> modelAdapter(LanguageModel)
    -> ai.generateText(...)
    -> Shared runCommerceTurn(...)
```

That path conflicts with ARCH-024:

- Admin owns Model Catalogue, Model Availability and the environment OpenRouter credential;
- Commerce Studio owns the one active model selection;
- ARCH-024-COMMERCE-002 defines the canonical Platform/Shop effective-model semantics;
- ARCH-024-SHARED-004 publishes the canonical model contracts and Node-only `OpenRouterModelClient` implementing the existing Shared `CommerceModelInvoker` boundary;
- `CommerceOpenRouterCredential` stores one encrypted OpenRouter credential per `CommerceEnvironment`.

Background remains the production CommerceAgent host. It MUST NOT import `moda-interact-commerce` source code. It consumes the same accepted database schema and Shared contracts and implements the production-side read of the canonical ARCH-024 selection rules exactly as specified below.

The current repository already contains a LangGraph wrapper in:

```text
src/agents/commerce.agent.pipeline.ts
```

That wrapper delegates to `runCommerceAgent` and is not the production worker entry path. Shared `runCommerceTurn` now owns the agreed Commerce-turn LangGraph refactor; dependent BACKGROUND-002 removes this redundant local wrapper after BACKGROUND-001 is accepted.

`GROQ_API_KEY` is also used by the independent WhatsApp speech-transcription path. This task MUST NOT remove or reinterpret that speech-transcription configuration merely because CommerceAgent model execution moves to OpenRouter.

ARCH-023 is frozen. Preserve whatever accepted Platform/Shop Instruction behaviour exists in the integrated baseline; do not redesign trusted-instruction semantics in this task.

## Scope

Primary implementation targets:

```text
moda-interact-background/database/                              # consume accepted DATABASE-001 gitlink
moda-interact-background/package.json
moda-interact-background/package-lock.json

moda-interact-background/src/agents/types.ts
moda-interact-background/src/agents/commerce.agent.ts
moda-interact-background/src/agents/commerce.agent.pipeline.ts  # validation only unless typing requires mechanical change
moda-interact-background/src/commerce/host.ts

moda-interact-background/src/commerce/model-environment.ts       # NEW
moda-interact-background/src/commerce/model-resolution.ts        # NEW
moda-interact-background/src/commerce/credential-keyring.ts      # NEW
moda-interact-background/src/commerce/openrouter-credential.ts   # NEW
moda-interact-background/src/commerce/production-model.ts        # NEW

moda-interact-background/src/services/checkout-recovery.service.ts
moda-interact-background/src/providers/groq.provider.ts          # DELETE when no references remain

moda-interact-background/tests/unit/agent/commerce.agent.configuration.test.ts
moda-interact-background/tests/unit/agent/commerce.agent.pipeline.test.ts
moda-interact-background/tests/unit/commerce/model-environment.test.ts            # NEW
moda-interact-background/tests/unit/commerce/model-resolution.test.ts             # NEW
moda-interact-background/tests/unit/commerce/openrouter-credential.test.ts         # NEW
moda-interact-background/tests/unit/commerce/production-model.test.ts              # NEW
moda-interact-background/tests/integration/commerce/host.test.ts

moda-interact-background/scripts/run-arch024-production-model-disposable.mjs       # NEW

moda-interact-background/README.md
moda-interact-background/docs/commerce-host.md
moda-interact-background/docs/commerceagent-sequence-diagrams/commerceagent-inner-loop.puml
```

Additional files may be changed only when mechanically required by the accepted Database/Shared dependency updates or to keep affected tests/docs accurate. List and justify every additional file in the Completion Report.

### Dependency consumption

This task MUST:

1. update the nested `database/` gitlink to the architect-accepted merged ARCH-024-DATABASE-001 database commit;
2. update `@modainteract/moda-interact-shared` to the **exact version published by ARCH-024-SHARED-004**;
3. update the Background lockfile with the repository's normal package manager;
4. run Prisma generation from the accepted nested schema;
5. consume `CommerceModelInvoker`, `ResolvedCommerceModelSchema` and `OpenRouterModelClient` from the published Shared package rather than recreating them locally.

Do not edit the nested database schema in this task.

Do not use a local Shared checkout, `npm link`, `file:` dependency or workspace borrowing in place of the published SHARED-004 package.

## Out of Scope

- Admin Model Catalogue, Availability or credential mutation UI.
- Commerce Studio model selection UI.
- Test Conversation/Preview execution; ARCH-024-COMMERCE-007 owns that path.
- Changing ARCH-024-COMMERCE-002 selection semantics.
- Merchant-facing model selection; merchants never select the model.
- LangGraph topology redesign, checkpointing or durable LangGraph state.
- Tool/Capability/Release selection or MCP authorization changes.
- Platform/Shop Instruction redesign from frozen ARCH-023.
- Speech-transcription provider migration.
- Removing `GROQ_API_KEY` while it remains required by speech transcription.
- Introducing `OPENROUTER_API_KEY`, `COMMERCE_OPENROUTER_API_KEY` or another plaintext model credential environment variable.
- Introducing a second encryption keyring.
- Live OpenRouter calls in automated validation.

## Requirements

### R1 — consume the canonical Shared runtime and remove the Background-local model adapter

Import production model runtime contracts from the exact SHARED-004 package.

At minimum use:

```text
@modainteract/moda-interact-shared/commerce/model
    CommerceEnvironment
    CommerceEnvironmentSchema
    CommerceModelAvailabilitySchema
    CommerceModelCatalogueEntrySchema
    ResolvedCommerceModel
    ResolvedCommerceModelSchema

@modainteract/moda-interact-shared/commerce/runner
    CommerceModelInvoker
    ModelRequest
    ModelStep

@modainteract/moda-interact-shared/commerce/model/node
    OpenRouterModelClient
    OpenRouterModelClientOptions
```

`src/commerce/host.ts` MUST accept `CommerceModelInvoker` directly.

Delete the Background-local `modelAdapter(model: LanguageModel)` implementation and remove its `generateText/jsonSchema/tool` model-bridge imports from `host.ts`.

Do not change `runCommerceTurn`, `ModelRequest`, `ModelStep`, Tool budgets, final-response behaviour or Tool execution semantics.

### R2 — resolve the Commerce environment deterministically

Create:

```text
src/commerce/model-environment.ts
```

Export exactly:

```ts
export function resolveCommerceEnvironment(): CommerceEnvironment;
```

Use the existing:

```ts
resolveDeploymentEnvironmentName()
```

from `src/runtime/deployment-environment.ts` as the deployment identity source.

Normalize only the following exact case-insensitive values:

```text
local        -> LOCAL
test         -> TEST
development  -> DEVELOPMENT
staging      -> STAGING
production   -> PRODUCTION
```

Validate the result with the published `CommerceEnvironmentSchema`.

Any other value is a bounded configuration error. Do not guess, default unknown values to PRODUCTION or derive a different environment from `NODE_ENV` separately from the existing deployment-environment resolver.

### R3 — make canonical `Shop.id` part of `RecoveryAgentContext`

Extend the local Background context shape exactly:

```ts
export interface RecoveryAgentContext {
  shopId: string;
  shop: string;
  // existing recovery/customer/conversation fields unchanged
}
```

Update `checkoutRecoveryService.getAgentContext(...)` to select and return the recovery's canonical `shopId` together with the existing Shop domain.

The existing `loadConversationTurn(...)`/recovery ownership path already resolves canonical Shop ownership. Do not derive Shop identity from the `.myshopify.com` domain.

In `executeCommerceHost(...)`, after loading the current Conversation/CheckoutRecovery, require:

```text
recovery.shopId === context.shopId
recovery.shop.domain === context.shop
```

A mismatch is a denied/stale turn and MUST occur before customer content is submitted to the model.

Update all affected fixtures/tests with explicit `shopId`; do not make the field optional merely to preserve old tests.

### R4 — implement the production effective-model resolver with the exact ARCH-024 semantics

Create:

```text
src/commerce/model-resolution.ts
```

Export exactly:

```ts
export async function resolveProductionCommerceModel(input: {
  db: PrismaClient;
  environment: CommerceEnvironment;
  shopId: string;
}): Promise<ResolvedCommerceModel>;
```

Execute the resolution in one Prisma transaction using `REPEATABLE READ`.

Within that transaction:

1. require the exact `Shop.id = shopId` to exist;
2. load at most the two `CommerceAgentConfiguration` rows for:
   - `scope = PLATFORM`, `shopId = NULL`, exact `environment`;
   - `scope = SHOP`, `shopId = input.shopId`, exact `environment`;
3. include each selected `CommerceModelCatalogueEntry` and its `CommerceModelAvailability`;
4. validate durable rows through the accepted Shared schemas before using them.

Apply this exact winner algorithm:

```text
IF Shop configuration exists AND Shop.modelId != NULL:
    validate that exact Shop-selected model
    DO NOT require Platform model to be valid first
    DO NOT fall back to Platform on failure
    winner = Shop-selected model

ELSE:
    require Platform configuration with non-null modelId
    validate Platform-selected model
    winner = Platform-selected model
```

A Platform-selected model is valid only when all are true:

```text
model.enabled = true
availability.enabled = true
availability.scope = PLATFORM
availability.shopId = NULL
```

An explicit Shop-selected model is valid only when all are true:

```text
model.enabled = true
availability.enabled = true
AND (
  availability.scope = PLATFORM AND availability.shopId = NULL
  OR
  availability.scope = SHOP AND availability.shopId = input.shopId
)
```

A Shop-selected model belonging to any other Shop is invalid.

Return exactly the published `ResolvedCommerceModel` shape and validate the final object with `ResolvedCommerceModelSchema` before returning it.

The returned provenance is the **availability provenance of the winning catalogue entry**:

```text
sourceScope  = winning availability.scope
sourceShopId = winning availability.shopId
```

Do not mutate or clear `CommerceAgentConfiguration.modelId` when resolution fails.

Missing Shop, missing selection, disabled model, disabled Availability, malformed persisted configuration, wrong-Shop Availability or database failure MUST fail bounded before model invocation. Never silently substitute another model.

### R5 — model selection is stable for one production turn

The effective model MUST be resolved exactly once for one `runCommerceAgent(context)` invocation.

If Commerce Studio changes the active model after a production turn has begun:

```text
current turn
    -> continues using the model resolved at turn start

next runCommerceAgent turn
    -> resolves the new active model
```

Do not re-query Agent Configuration before every model call inside the same `runCommerceTurn` loop.

This rule stabilizes authored model identity/configuration for one production turn without creating new durable snapshot tables.

### R6 — parse only the existing Commerce credential keyring

Create:

```text
src/commerce/credential-keyring.ts
```

Export exactly:

```ts
export function readCommerceCredentialKeyring(): Readonly<Record<string, Uint8Array>>;
```

Read only:

```text
COMMERCE_CONNECTION_KEYS_JSON
```

The value MUST parse as a JSON object whose keys are nonblank key IDs and whose values are base64 strings decoding to exactly 32 bytes.

Reject malformed JSON, non-object values, blank key IDs, invalid base64 or non-32-byte keys with a bounded configuration error.

Never log the raw environment value, base64 key material or decoded keys.

Do not require:

```text
COMMERCE_CONNECTION_ACTIVE_KEY_ID
COMMERCE_CONNECTION_COMMAND_HMAC_KEY
```

for model invocation. Those settings belong to credential mutation/External Connection workflows, not OpenRouter decryption.

Do not create a second encryption root for Background.

### R7 — decrypt the current environment OpenRouter credential exactly

Create:

```text
src/commerce/openrouter-credential.ts
```

Export:

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
2. query the unique `CommerceOpenRouterCredential` row for the exact environment;
3. require the row to exist;
4. require `keyring[row.keyId]` to exist and contain exactly 32 bytes;
5. require the persisted envelope to satisfy DATABASE-001 constraints;
6. decrypt with AES-256-GCM using stored 12-byte nonce and 16-byte auth tag;
7. use this exact UTF-8 AAD:

```ts
canonicalJson({
  credentialType: "OPENROUTER",
  environment,
  keyId: row.keyId,
})
```

8. require decrypted plaintext to be 1..8192 UTF-8 bytes and contain no `\r`, `\n` or `\0`;
9. return the exact plaintext credential;
10. map missing row, missing key, malformed envelope, authentication failure, database failure or invalid plaintext to one bounded `UNAVAILABLE`/configuration failure without leaking detail.

Do not cache the decrypted credential.

This is the same sealed-secret/AAD contract owned by ARCH-024-ADMIN-003 and consumed by ARCH-024-COMMERCE-007.

### R8 — create one production model invoker with fixed model configuration and live credential resolution

Create:

```text
src/commerce/production-model.ts
```

Export equivalent public testable shapes:

```ts
export type ProductionOpenRouterModelFactory =
  (options: OpenRouterModelClientOptions) => CommerceModelInvoker;

export async function createProductionCommerceModelInvoker(input: {
  db: PrismaClient;
  environment: CommerceEnvironment;
  shopId: string;
  credentialResolver: OpenRouterCredentialResolver;
  createClient?: ProductionOpenRouterModelFactory;
}): Promise<CommerceModelInvoker>;
```

`createProductionCommerceModelInvoker(...)` MUST:

1. resolve the effective model once through `resolveProductionCommerceModel(...)`;
2. retain only the resolved non-secret model identity/configuration for the returned invoker;
3. default `createClient` to:

```ts
(options) => new OpenRouterModelClient(options)
```

4. on **every** returned `invoke(request, signal)` call:
   - fail if signal is aborted;
   - resolve the current environment OpenRouter credential using `credentialResolver.resolve(...)`;
   - construct a fresh `OpenRouterModelClient` from the fixed resolved model's exact `provider`, `providerModelId`, `configurationSchemaVersion`, `configuration` plus the just-resolved credential;
   - delegate the exact existing `ModelRequest` and `AbortSignal`;
   - return the exact `ModelStep`;
5. never persist/cache plaintext credential or an `OpenRouterModelClient` across model invocations.

Required behaviour:

```text
turn starts with model M
model invocation 1 -> credential A
Admin replaces A with B
model invocation 2 -> credential B

Admin changes active model M to N during same turn
model invocation 2 -> still model M
next CommerceAgent turn -> model N
```

### R9 — `runCommerceAgent` must use the production resolver path and preserve test injection

Refactor `src/agents/commerce.agent.ts` so the production path no longer reads:

```text
GROQ_COMMERCE_MODEL
```

and no longer imports `groq.provider.ts`.

The normal production path MUST:

```text
resolveCommerceEnvironment()
        ↓
readCommerceCredentialKeyring()
        ↓
createOpenRouterCredentialResolver({ db: prisma, keyring })
        ↓
createProductionCommerceModelInvoker({
    db: prisma,
    environment,
    shopId: context.shopId,
    credentialResolver,
})
        ↓
executeCommerceHost(context, { model, signal? })
```

Preserve bounded dependency injection for tests. `CommerceAgentDependencies.model`, when explicitly supplied, MUST be a `CommerceModelInvoker` and MUST bypass production model/credential resolution for that invocation.

Do not retain `LanguageModel` or provider-SDK types in the `runCommerceAgent` public dependency contract.

### R10 — remove the obsolete Groq CommerceAgent provider without breaking voice transcription

After all CommerceAgent references are removed:

```text
DELETE src/providers/groq.provider.ts
```

Remove `@ai-sdk/groq` from `package.json`/lockfile if and only if no remaining Background source/test imports it.

Remove all CommerceAgent references to:

```text
GROQ_COMMERCE_MODEL
```

from source, tests and Background-owned CommerceAgent documentation.

Do **not** remove or rename:

```text
GROQ_API_KEY
GROQ_TRANSCRIPTION_MODEL
WHATSAPP_TRANSCRIPTION_PROVIDER
```

where they remain part of the independent speech-transcription service.

Do not opportunistically migrate speech transcription to OpenRouter.

### R11 — preserve production worker topology; Shared now owns Commerce-turn LangGraph

The WhatsApp worker continues to invoke the production CommerceAgent through the current conversation-turn/admission path. The published Shared `runCommerceTurn` now owns the actual low-level LangGraph state machine.

Do not add Background-local graph nodes, checkpoints, memory, durable threads, new worker queues or new conversation-ordering semantics.

The pre-existing one-node `createCommerceAgentPipeline(...)` wrapper is not production orchestration and is removed by dependent `ARCH-024-BACKGROUND-002` after this task is accepted. This task may make only mechanical typing changes required to keep it compiling until that cleanup executes.

### R12 — preserve current host/MCP and trusted-instruction behaviour

This task changes the model dependency passed into `runCommerceTurn` and wires the existing host `StructuredLogger` into the new optional runner logger dependency. It does not change Tool/MCP business semantics.

Do not change:

```text
Commerce grant resolution
MCP manifest pinning
Tool authorization
Tool execution
Feature Behaviour ordering
response-contract handling
conversation history
turn lease/staleness checks
finalResponse validation
outbound WhatsApp admission/delivery
```

Preserve the accepted integrated ARCH-023 Platform/Shop Instruction behaviour if present when this task executes. Do not reimplement or reorder that architecture in this task.

### R13 — errors and secrets are bounded

The following must never be emitted in logs, telemetry, thrown public messages or persisted model state:

```text
OpenRouter API credential
credential ciphertext
nonce
authTag
key material/base64 keyring
Authorization header
raw provider response body
raw LangChain/OpenRouter exception containing provider payload
```

Configuration/model-resolution/decryption/provider failures must surface through the existing bounded CommerceAgent/CommerceHost failure boundary and MUST NOT expose provider details to the customer.

Do not log model configuration JSON wholesale; log only bounded identifiers such as model catalogue entry ID/provider/providerModelId when operationally required and already permitted by existing structured logging policy.

### R14 — production code must not depend directly on LangChain/OpenRouter packages

Background MUST instantiate only the Shared-published:

```text
OpenRouterModelClient
```

It MUST NOT add/import:

```text
@langchain/openrouter
@langchain/core
```

in Background production source.

Background production source MUST NOT add any new LangGraph usage. The pre-existing wrapper/dependency is removed by ARCH-024-BACKGROUND-002 after this migration is accepted.

### R14A — retain `CommerceMcpClient` and inject the canonical Shared logger into `runCommerceTurn`

The MCP decision is closed for ARCH-024. Retain:

```text
src/commerce/mcp-client.ts
CommerceMcpClient
@modelcontextprotocol/sdk
```

Do not add `@langchain/mcp-adapters` and do not move MCP transport into Shared.

Background must use the canonical Shared logging API:

```ts
import {
  createLogger,
  type StructuredLogger,
} from "@modainteract/moda-interact-shared/logging";
```

Extend bounded test injection as needed so `runCommerceAgent`/`executeCommerceHost` can receive a `StructuredLogger`. The production default must preserve the actual executing service identity (currently the messaging worker path), not create a `moda-interact-shared` identity.

When invoking `runCommerceTurn`, pass a child logger containing only safe host context, for example:

```ts
logger: hostLogger.child({
  component: "commerce-agent-host",
  recoveryId: recovery.id,
  conversationId: current.id,
})
```

The Shared runner will add its own `component: "commerce-turn-runner"` child context. Do not include customer name/message content, Tool arguments/results, Merchant Knowledge content, provider payloads or credentials in the host logger.

Add regression coverage proving Background passes a logger to the runner and MCP/runner failures remain bounded without logging sensitive content.

### R15 — focused model-resolution tests are mandatory

Add deterministic unit tests proving at least:

1. Shop with no override uses valid Platform-selected model.
2. Shop with explicit valid Platform-availability model uses that explicit model.
3. Shop with explicit valid own-Shop-availability model uses that explicit model.
4. Valid explicit Shop model works even when Platform selection is missing/broken.
5. Explicit Shop model in another Shop's Availability fails closed.
6. Explicit disabled Shop model fails closed with no Platform fallback.
7. Explicit model in disabled Availability fails closed.
8. Missing Platform selection fails when Shop has no override.
9. Disabled Platform model fails when Shop has no override.
10. Malformed persisted configuration fails validation before client construction.
11. Missing Shop ID fails rather than treating the request as Platform-only.
12. Resolution result validates through `ResolvedCommerceModelSchema`.
13. availability provenance in the resolved shape is correct for Platform vs Shop catalogue entries.
14. Agent Configuration is not mutated/cleared by resolution failures.

### R16 — credential/model-invoker tests are mandatory

Add deterministic tests proving:

1. keyring parser accepts valid 32-byte base64 keys;
2. malformed JSON/base64/key length is rejected without logging secret material;
3. credential resolver decrypts an ADMIN-003-compatible AES-GCM envelope;
4. missing credential row fails bounded;
5. missing key ID fails bounded;
6. auth-tag mismatch fails bounded;
7. invalid plaintext length/control characters fail bounded;
8. every model `invoke` resolves credential anew;
9. credential A -> B replacement is observed by the next invocation;
10. fixed model identity/configuration remains unchanged across invocations in one turn;
11. cancellation propagates through credential/client invocation;
12. fake `createClient` receives exact provider/providerModelId/configuration/credential and no unexpected values.

No unit/integration test may call the live OpenRouter API.

### R17 — `runCommerceAgent` and host regressions are mandatory

Update/replace the old `GROQ_COMMERCE_MODEL` configuration tests.

Tests MUST prove:

1. explicit injected `CommerceModelInvoker` bypasses production database/keyring resolution;
2. production path no longer reads `GROQ_COMMERCE_MODEL`;
3. host accepts `CommerceModelInvoker` directly and no local `LanguageModel` adapter remains;
4. current turn Shop ID/domain mismatch is denied before model invocation;
5. the production WhatsApp/conversation-turn path still delegates to `runCommerceAgent` without using the optional one-node wrapper;
6. `runCommerceTurn` receives a host-created `StructuredLogger` preserving `service.name=moda-messaging-worker` (or the canonical executing process identity) plus safe host context;
7. existing Commerce host MCP/grant/tool/final-response tests continue to pass.

### R18 — a disposable PostgreSQL proof is mandatory

Create:

```text
scripts/run-arch024-production-model-disposable.mjs
```

The script MUST create and destroy its own disposable PostgreSQL container/network using the accepted ARCH-024 database schema.

It MUST NOT use the developer's normal database.

The proof must:

1. create one Platform Admin required by credential provenance;
2. create two Shops: `shop-a`, `shop-b`;
3. create enabled Platform Availability and enabled exact-Shop Availability for `shop-a`;
4. create Platform model `platform-model` and private Shop A model `shop-a-model` with valid Shared configuration JSON;
5. create DEVELOPMENT Platform Agent Configuration selecting `platform-model`;
6. create DEVELOPMENT Shop A Agent Configuration with `modelId = NULL` and prove Platform inheritance;
7. set Shop A explicit selection to `shop-a-model` and prove exact-Shop winner;
8. prove Shop B cannot treat `shop-a-model` as valid;
9. seal and insert OpenRouter credential `credential-A` with the exact ADMIN-003/C007 AAD/keyring contract;
10. create the production model invoker with an injected fake Shared client factory and prove model invocation receives `credential-A` plus the expected selected model;
11. replace the database credential with sealed `credential-B` without recreating the production invoker;
12. invoke again and prove the fake client receives `credential-B` while the model identity/configuration remains unchanged;
13. change the Shop's active model after the invoker was created and prove the existing invoker still uses the original per-turn model;
14. create a **new** production invoker and prove it resolves the newly active model;
15. remove/disable the explicit selected model and prove a new resolver invocation fails closed rather than silently inheriting Platform;
16. clean up every task-owned container/network in `finally`.

Do not print decrypted credentials to stdout/stderr. Assertions compare them only in process memory.

The script MUST NOT call OpenRouter.

### R19 — static cleanup assertions are mandatory

Validation MUST prove there are no remaining CommerceAgent source/test/doc references to:

```text
GROQ_COMMERCE_MODEL
src/providers/groq.provider
modelAdapter(
```

except historical migration/decision documentation outside the Background repository when not owned by this task.

Validation MUST separately prove that legitimate speech-transcription references to `GROQ_API_KEY` remain intact.

Validation MUST prove Background production source contains no import from:

```text
@langchain/openrouter
@langchain/core
```

### R20 — update Background-owned runtime documentation only

Update `README.md`, `docs/commerce-host.md` and the CommerceAgent inner-loop sequence diagram to describe:

```text
Commerce Studio selection
    -> CommerceAgentConfiguration
    -> effective Platform/Shop model resolution per production turn
    -> current environment OpenRouter credential per model invocation
    -> Shared OpenRouterModelClient
    -> OpenRouter
```

Documentation MUST explicitly state:

- one effective active model per Shop;
- model selection is stable for one production turn;
- OpenRouter credential is live per invocation;
- `GROQ_COMMERCE_MODEL` is no longer a CommerceAgent requirement;
- `GROQ_API_KEY` may still be required independently for Groq speech transcription.

Do not document ARCH-024 Test Conversations as Background runtime behaviour.

## Work Items

- [ ] Consume the accepted ARCH-024 Database gitlink and exact SHARED-004 package version.
- [ ] Add canonical deployment-to-Commerce environment resolution.
- [ ] Add canonical `shopId` to `RecoveryAgentContext` and populate it from durable ownership.
- [ ] Implement the exact production effective-model resolver from R4.
- [ ] Implement the existing Commerce credential-keyring parser from `COMMERCE_CONNECTION_KEYS_JSON`.
- [ ] Implement AES-256-GCM OpenRouter credential resolution using the exact ADMIN-003/C007 AAD contract.
- [ ] Implement the per-turn fixed-model/per-invocation-live-credential production model invoker.
- [ ] Refactor `runCommerceAgent` to use the dynamic OpenRouter production path while retaining explicit test injection.
- [ ] Refactor `executeCommerceHost` to accept `CommerceModelInvoker` directly and remove the local AI-SDK model adapter.
- [ ] Delete the obsolete CommerceAgent Groq provider and remove `@ai-sdk/groq` only if no remaining references exist.
- [ ] Preserve Groq speech-transcription environment requirements.
- [ ] Add focused model-resolution, credential, model-invoker, agent and host regressions.
- [ ] Add and pass the disposable PostgreSQL selection + credential-rotation proof.
- [ ] Update Background-owned CommerceAgent runtime documentation.
- [ ] Run all required validation and record exact results/warnings in the Completion Report.

## Interfaces / Contracts

### Contract owner — ARCH-024 model contracts/runtime

Task:

`ARCH-024-SHARED-001` / publication `ARCH-024-SHARED-004`

Package:

```text
@modainteract/moda-interact-shared
```

Consumed browser/runtime-safe model contracts include:

```text
CommerceEnvironment
CommerceEnvironmentSchema
CommerceModelAvailabilitySchema
CommerceModelCatalogueEntrySchema
ResolvedCommerceModel
ResolvedCommerceModelSchema
```

Consumed runner/runtime exports include:

```text
CommerceModelInvoker
ModelRequest
ModelStep
OpenRouterModelClient
OpenRouterModelClientOptions
```

### Durable state owner

`ARCH-024-DATABASE-001`

Background consumes:

```text
commerce.CommerceModelAvailability
commerce.CommerceModelCatalogueEntry
commerce.CommerceAgentConfiguration
commerce.CommerceOpenRouterCredential
commerce.Shop
```

### Effective model semantic contract

`ARCH-024-COMMERCE-002` defines the canonical Platform/Shop selection semantics consumed by Studio/Test Conversations.

Background MUST implement the exact same architect-defined semantics from R4 for production execution because Background is a separate deployable/repository and MUST NOT import private Commerce source code.

Any discrepancy discovered between the accepted C002 semantics and this task is an architectural conflict: STOP and return it to `moda_architect`; do not invent another fallback rule.

### Credential sealing contract

Producer/administrator:

`ARCH-024-ADMIN-003`

Consumers:

```text
ARCH-024-COMMERCE-007
ARCH-024-BACKGROUND-001
```

Exact encryption contract:

```text
AES-256-GCM
keyring = COMMERCE_CONNECTION_KEYS_JSON
nonce = persisted 12 bytes
authTag = persisted 16 bytes
AAD = canonicalJson({
  credentialType: "OPENROUTER",
  environment,
  keyId,
})
```

No plaintext credential crosses repository boundaries.

## Dependencies

- `ARCH-024-DATABASE-001`
- `ARCH-024-SHARED-004`
- `ARCH-024-COMMERCE-002`
- `ARCH-024-ADMIN-003`

All dependencies must be architect-accepted Complete before this task becomes Ready.

## Enables

- `ARCH-024-GATEWAY-001`

Terminal ARCH-024 system-test tasks may also depend on this task when they are materialised. Do not add a dependency from this implementation task to a system-test task.

## Acceptance Criteria

- [ ] Production CommerceAgent no longer reads `GROQ_COMMERCE_MODEL` or constructs the conversational model through `src/providers/groq.provider.ts`.
- [ ] Production model selection resolves exactly one effective active model from current Agent Configuration and Availability for the trusted Shop/environment.
- [ ] An explicit valid Shop override does not depend on a valid Platform model.
- [ ] An explicit broken Shop override fails closed and never silently falls back to Platform.
- [ ] A Shop with no override inherits the valid Platform selection.
- [ ] The resolved model identity/configuration is stable for one `runCommerceAgent` turn and a new turn observes a later selection change.
- [ ] Every model invocation resolves/decrypts the current environment OpenRouter credential and therefore observes credential replacement without worker restart.
- [ ] No plaintext OpenRouter credential is persisted, cached process-wide, logged or included in model/configuration state.
- [ ] Background uses the published Shared `OpenRouterModelClient`/`CommerceModelInvoker` boundary and has no direct `@langchain/openrouter` or `@langchain/core` production dependency.
- [ ] `executeCommerceHost` no longer contains the Background-local `LanguageModel -> ModelStep` adapter.
- [ ] `RecoveryAgentContext` carries canonical Shop ID and host validation rejects Shop ID/domain mismatch before model invocation.
- [ ] Production worker/admission topology is unchanged; Shared owns Commerce-turn LangGraph and BACKGROUND-002 owns deletion of the redundant local wrapper.
- [ ] Existing MCP grant/Tool/response-contract/turn-staleness semantics remain unchanged.
- [ ] `GROQ_API_KEY` speech-transcription behaviour remains intact and is not conflated with CommerceAgent OpenRouter authentication.
- [ ] Missing/malformed model configuration or credential fails through a bounded non-secret error path.
- [ ] No automated test makes a live OpenRouter request.
- [ ] Disposable PostgreSQL proof demonstrates Platform inheritance, exact-Shop override, cross-Shop denial, credential A -> B live rotation and next-turn model-selection refresh.
- [ ] Background-owned CommerceAgent documentation describes the final dynamic model path accurately.

## Validation

Before running Node commands, follow the repository's package scripts and workspace Node bootstrap policy.

Required checks:

- [ ] Inspect current `package.json` scripts before validation; do not invent missing repository scripts.
- [ ] `npm run prisma:validate`
- [ ] `npm run prisma:generate`
- [ ] Focused unit tests:

```bash
npm test -- \
  tests/unit/commerce/model-environment.test.ts \
  tests/unit/commerce/model-resolution.test.ts \
  tests/unit/commerce/openrouter-credential.test.ts \
  tests/unit/commerce/production-model.test.ts \
  tests/unit/agent/commerce.agent.configuration.test.ts \
  tests/unit/agent/commerce.agent.pipeline.test.ts
```

- [ ] Existing Commerce host integration regression:

```bash
npm test -- tests/integration/commerce/host.test.ts
```

- [ ] Existing speech-transcription regression proving legitimate Groq transcription configuration remains valid:

```bash
npm test -- tests/unit/services/speech-transcription.service.test.ts
```

- [ ] Disposable PostgreSQL proof:

```bash
node scripts/run-arch024-production-model-disposable.mjs
```

- [ ] TypeScript production build:

```bash
npm run build
```

- [ ] Repository test suite required by the implementing agent's normal completion policy, with any known baseline failures identified by durable baseline ID rather than silently ignored.
- [ ] Static assertions equivalent to:

```bash
! grep -R "GROQ_COMMERCE_MODEL" src tests README.md docs/commerce-host.md docs/commerceagent-sequence-diagrams/commerceagent-inner-loop.puml
! grep -R "src/providers/groq.provider\|providers/groq.provider" src tests
! grep -R "modelAdapter(" src tests
! grep -R "@langchain/openrouter\|@langchain/core" src

grep -R "GROQ_API_KEY" src/services/speech-transcription.service.ts
```

- [ ] `git diff --check`
- [ ] Changed-file diagnostics contain zero task-owned TypeScript errors.

No validation command may call OpenRouter or any other live conversational LLM provider.

Record every command, pass/fail count, warning and baseline reference in the Completion Report.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

1. finish the Completion Report;
2. set this task to `review`;
3. clear no dependency state outside this assigned task;
4. return control to `moda_architect`;
5. **STOP**.

Do not begin Gateway or system-test work.

## Implementation Notes

- The duplicated production-side database read is intentional at this repository boundary: Background cannot import Commerce private source. The semantic contract is architect-owned and must match accepted ARCH-024-COMMERCE-002 exactly. If that proves impractical or drift is discovered, stop and return the architecture issue rather than inventing a third rule.
- Model configuration is fixed per production turn; credential state is intentionally live per model invocation.
- `COMMERCE_CONNECTION_KEYS_JSON` is reused as the encryption root. Do not introduce a provider-specific keyring.
- `GROQ_API_KEY` remains a valid independent speech-transcription secret after the conversational model moves to OpenRouter.
- `@langchain/langgraph` is already present in Background and remains unrelated to the model-provider migration in this task.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
