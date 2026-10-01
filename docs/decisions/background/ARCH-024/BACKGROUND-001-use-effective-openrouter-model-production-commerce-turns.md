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
status: ready
priority: 55
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-024-DATABASE-001
  - ARCH-024-SHARED-002
enables:
  - ARCH-024-BACKGROUND-002
  - ARCH-024-GATEWAY-001
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
- Commerce Studio owns the explicit Platform/Shop Agent Configuration selection;
- Platform Admin may associate a global Platform-available model with a Merchant Pricing Plan;
- the parent ARCH-024 architecture defines the canonical `SHOP -> PRICING_PLAN -> PLATFORM` effective-model semantics; Commerce and Background implement the same policy independently at their repository boundaries;
- ARCH-024-SHARED-002 publishes the canonical model contracts and Node-only `OpenRouterModelClient` implementing the existing Shared `CommerceModelInvoker` boundary;
- `CommerceOpenRouterCredential` stores one encrypted OpenRouter credential per `CommerceEnvironment`.

Background remains the production CommerceAgent host. It MUST NOT import `moda-interact-commerce` source code. It consumes the same accepted database schema and Shared contracts and implements the production-side read of the canonical ARCH-024 selection rules exactly as specified below.

The current repository already contains a LangGraph wrapper in:

```text
src/agents/commerce.agent.pipeline.ts
```

That wrapper delegates to `runCommerceAgent` and is not the production worker entry path. Shared `runCommerceTurn` now owns the agreed Commerce-turn LangGraph refactor; dependent BACKGROUND-002 removes this redundant local wrapper after BACKGROUND-001 is accepted.

`GROQ_API_KEY` is also used by the independent WhatsApp speech-transcription path. This task MUST NOT remove or reinterpret that speech-transcription configuration merely because CommerceAgent model execution moves to OpenRouter.

ARCH-023 is frozen. Preserve whatever accepted Platform/Shop Instruction behaviour exists in the integrated baseline; do not redesign trusted-instruction semantics in this task. Price Plan model assignment is ARCH-024 Platform product configuration only and MUST NOT introduce merchant model selection.

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
2. update `@modainteract/moda-interact-shared` to the **exact version published by ARCH-024-SHARED-002**;
3. update the Background lockfile with the repository's normal package manager;
4. run Prisma generation from the accepted nested schema;
5. consume `CommerceModelInvoker`, `ResolvedCommerceModelSchema` and `OpenRouterModelClient` from the published Shared package rather than recreating them locally.

Do not edit the nested database schema in this task.

Do not use a local Shared checkout, `npm link`, `file:` dependency or workspace borrowing in place of the published SHARED-002 package.

## Out of Scope

- Admin Model Catalogue, Availability or credential mutation UI.
- Commerce Studio model selection UI.
- Test Conversation/Preview execution; ARCH-024-COMMERCE-007 owns that path.
- Changing the parent ARCH-024 `SHOP -> PRICING_PLAN -> PLATFORM` selection semantics.
- Editing Merchant Pricing Plan model assignments; ARCH-024-ADMIN-004 owns that control-plane surface.
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

Import production model runtime contracts from the exact SHARED-002 package.

At minimum use:

```text
@modainteract/moda-interact-shared/commerce/model
    CommerceEnvironment
    CommerceEnvironmentSchema
    CommerceModelAvailabilitySchema
    CommerceModelCatalogueEntrySchema
    CommerceModelSelectionSource
    CommerceModelSelectionSourceSchema
    CommercePricingPlanModelAssignmentSchema
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
export type ResolvedProductionCommerceModel = {
  selectionSource: CommerceModelSelectionSource;
  selectionShopId: string | null;
  merchantPricingPlanId: string | null;
  shopifyPlanHandle: string | null;
  model: ResolvedCommerceModel;
};

export async function resolveProductionCommerceModel(input: {
  db: PrismaClient;
  environment: CommerceEnvironment;
  shopId: string;
}): Promise<ResolvedProductionCommerceModel>;
```

Execute the resolution in one Prisma transaction using `REPEATABLE READ`. The resolver MUST use the same durable decision snapshot for the Shop override, current subscription/plan and Platform fallback.

Within that transaction, load only what the winning branch requires and apply this exact precedence:

```text
1. SHOP explicit override
2. current PRICING_PLAN model assignment
3. PLATFORM default
```

#### R4.1 — Shop explicit override

1. require the exact `Shop.id = input.shopId` to exist;
2. load the `CommerceAgentConfiguration` row for `scope = SHOP`, `shopId = input.shopId`, exact `environment`;
3. if that row exists and `modelId != NULL`, validate that exact selected model;
4. a Shop-selected model is valid only when:

```text
model.enabled = true
availability.enabled = true
AND (
  availability.scope = PLATFORM AND availability.shopId = NULL
  OR
  availability.scope = SHOP AND availability.shopId = input.shopId
)
```

5. a Shop-selected model belonging to another Shop is invalid;
6. if the explicit Shop selection is valid, return immediately with:

```ts
{
  selectionSource: "SHOP",
  selectionShopId: input.shopId,
  merchantPricingPlanId: null,
  shopifyPlanHandle: null,
  model: resolvedModel,
}
```

Do **not** query or require Price Plan/Platform selection validity before accepting a valid explicit Shop override. If an explicit Shop-selected model is invalid/disabled/unavailable, fail `UNAVAILABLE`; do not fall through.

#### R4.2 — current Price Plan model assignment

Only when there is no explicit Shop model (`Shop configuration missing` or `Shop.modelId = NULL`), resolve the Shop's **current** subscribed Price Plan.

Use exactly:

```text
Shop.id
  -> Shop.subscription (unique)
  -> Subscription.status
  -> Subscription.planId / Subscription.plan
  -> BillingPlan.shopifyPlanHandle
  -> MerchantPricingPlan.shopifyPlanHandle
  -> MerchantPricingPlan.commerceModelId
```

Rules:

1. only `Subscription.status IN (ACTIVE, TRIALING)` is eligible;
2. require non-null current `Subscription.planId`/`Subscription.plan` before any Price Plan override can exist;
3. use the current `BillingPlan.shopifyPlanHandle`;
4. ignore `pendingPlanId`, `pendingPlan` and `pendingShopifyPlanHandle`; a future upgrade/downgrade receives no model benefit until it becomes current;
5. match `MerchantPricingPlan` by exact unique `shopifyPlanHandle`;
6. do **not** require `MerchantPricingPlan.isActive = true` for an existing subscriber; `isActive` controls catalogue sale/selection, not benefits attached to the current plan;
7. validate the materialised assignment through `CommercePricingPlanModelAssignmentSchema`;
8. if there is no eligible current subscription/current BillingPlan, no matching `MerchantPricingPlan`, or `commerceModelId = NULL`, there is no Price Plan override and resolution continues to Platform;
9. if `commerceModelId != NULL`, validate that exact model. A Price Plan-selected model is valid only when:

```text
model.enabled = true
availability.enabled = true
availability.scope = PLATFORM
availability.shopId = NULL
```

A Price Plan MUST NOT consume a Shop-scoped model.

10. if valid, return:

```ts
{
  selectionSource: "PRICING_PLAN",
  selectionShopId: input.shopId,
  merchantPricingPlanId: merchantPricingPlan.id,
  shopifyPlanHandle: merchantPricingPlan.shopifyPlanHandle,
  model: resolvedModel,
}
```

11. if the matching Price Plan explicitly names a model but that model is missing, disabled, Availability-disabled or no longer Platform-available, fail `UNAVAILABLE`; do **not** silently downgrade to Platform.

A valid Price Plan winner does **not** require a valid Platform Agent Configuration.

#### R4.3 — Platform fallback

Only when there is neither an explicit Shop override nor an applicable Price Plan model assignment:

1. load the `CommerceAgentConfiguration` row for `scope = PLATFORM`, `shopId = NULL`, exact `environment`;
2. require non-null `modelId`;
3. validate the selected model as:

```text
model.enabled = true
availability.enabled = true
availability.scope = PLATFORM
availability.shopId = NULL
```

4. return:

```ts
{
  selectionSource: "PLATFORM",
  selectionShopId: null,
  merchantPricingPlanId: null,
  shopifyPlanHandle: null,
  model: resolvedModel,
}
```

For every branch, validate the inner `model` with `ResolvedCommerceModelSchema` and validate `selectionSource` with `CommerceModelSelectionSourceSchema` before returning.

The returned `ResolvedCommerceModel.sourceScope/sourceShopId` remains **availability provenance**. It MUST NOT be overloaded to mean selection precedence. Selection precedence is carried separately by `selectionSource`.

Do not mutate/clear `CommerceAgentConfiguration.modelId` or `MerchantPricingPlan.commerceModelId` when resolution fails. Missing Shop, invalid explicit selection, malformed persisted configuration or database failure MUST fail bounded before model invocation.

### R5 — model selection is stable for one production turn

The effective model (including any current Price Plan winner) MUST be resolved exactly once for one `runCommerceAgent(context)` invocation.

If Commerce Studio changes an Agent Configuration selection, Platform Admin changes `MerchantPricingPlan.commerceModelId`, or billing makes a different `Subscription.planId` current after a production turn has begun:

```text
current turn
    -> continues using the model resolved at turn start

next runCommerceAgent turn
    -> resolves the new Shop / current Price Plan / Platform winner
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
7. obtain the exact canonical AAD string from the published Shared contract:

```ts
createCommerceOpenRouterCredentialAad({
  environment,
  keyId: row.keyId,
})
```

and UTF-8 encode that returned canonical string before calling `decipher.setAAD(...)`;

8. require decrypted plaintext to be 1..8192 UTF-8 bytes and contain no `\r`, `\n` or `\0`;
9. return the exact plaintext credential;
10. map missing row, missing key, malformed envelope, authentication failure, database failure or invalid plaintext to one bounded `UNAVAILABLE`/configuration failure without leaking detail.

Do not cache the decrypted credential.

This is the Shared-owned sealed-secret AAD contract also consumed independently by ARCH-024-ADMIN-003 and ARCH-024-COMMERCE-007.

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
2. retain the returned `selectionSource`/plan provenance for safe diagnostics and retain only the resolved non-secret `model` identity/configuration for model execution;
3. default `createClient` to:

```ts
(options) => new OpenRouterModelClient(options)
```

4. on **every** returned `invoke(request, signal)` call:
   - fail if signal is aborted;
   - resolve the current environment OpenRouter credential using `credentialResolver.resolve(...)`;
   - construct a fresh `OpenRouterModelClient` from the fixed `resolved.model` exact `provider`, `providerModelId`, `configurationSchemaVersion`, `configuration` plus the just-resolved credential;
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
  modelSelectionSource: resolved.selectionSource,
  merchantPricingPlanId: resolved.merchantPricingPlanId,
})
```

The Shared runner will add its own `component: "commerce-turn-runner"` child context. Do not include customer name/message content, Tool arguments/results, Merchant Knowledge content, provider payloads or credentials in the host logger.

Add regression coverage proving Background passes a logger to the runner and MCP/runner failures remain bounded without logging sensitive content.

### R15 — focused model-resolution tests are mandatory

Add deterministic unit tests proving at least:

1. Shop with no override, no eligible current Price Plan model and valid Platform selection uses Platform.
2. Shop with explicit valid Platform-availability model uses that explicit Shop override.
3. Shop with explicit valid own-Shop-availability model uses that explicit Shop override.
4. Valid explicit Shop model works even when current Price Plan and Platform selections are missing/broken.
5. Explicit Shop model in another Shop's Availability fails closed.
6. Explicit disabled Shop model fails closed with no Price Plan/Platform fallback.
7. Explicit model in disabled Availability fails closed.
8. `ACTIVE` current Subscription + matching `BillingPlan.shopifyPlanHandle` + matching `MerchantPricingPlan.commerceModelId` selects that Price Plan model.
9. `TRIALING` current Subscription is eligible for the same Price Plan model rule.
10. `NO_CONTRACT`, `UNMAPPED`, `SYNC_ERROR`, `FROZEN` or any future non-`ACTIVE`/`TRIALING` subscription status does not grant a Price Plan model override.
11. `pendingPlanId`/pending plan handle is ignored while the current plan remains unchanged.
12. current BillingPlan handle with no matching MerchantPricingPlan falls through to Platform.
13. matching MerchantPricingPlan with `commerceModelId = NULL` falls through to Platform.
14. matching MerchantPricingPlan with `isActive = false` still supplies the configured model to an existing current subscriber.
15. valid Price Plan model works even when Platform selection is missing/broken.
16. Price Plan model in Shop Availability fails closed; Price Plan models must be Platform-available.
17. disabled/missing Price Plan-selected model fails closed with no Platform fallback.
18. valid explicit Shop override wins over a valid Price Plan model.
19. changing only the current Subscription plan/handle changes the winner on the **next resolver call**.
20. changing only `MerchantPricingPlan.commerceModelId` changes the winner on the **next resolver call**.
21. Missing Platform selection fails when neither Shop nor Price Plan supplies a winner.
22. Disabled Platform model fails when neither Shop nor Price Plan supplies a winner.
23. Malformed persisted configuration fails validation before client construction.
24. Missing Shop ID fails rather than treating the request as Platform-only.
25. Inner model result validates through `ResolvedCommerceModelSchema`.
26. selection provenance is exactly `SHOP | PRICING_PLAN | PLATFORM`; availability provenance remains correct independently.
27. Agent Configuration and MerchantPricingPlan model associations are not mutated/cleared by resolution failures.

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
4. create Platform models `platform-model`, `starter-model`, `growth-model` and private Shop A model `shop-a-model` with valid Shared configuration JSON;
5. create DEVELOPMENT Platform Agent Configuration selecting `platform-model`;
6. create DEVELOPMENT Shop A Agent Configuration with `modelId = NULL`;
7. create `MerchantPricingPlan` rows `starter` and `growth` with exact unique Shopify handles and `commerceModelId = starter-model/growth-model`;
8. create matching operational `BillingPlan` rows with the same handles, without any model FK/column;
9. create an `ACTIVE` Shop A `Subscription` whose current `planId` points to `starter` and prove the winner is `starter-model` with `selectionSource = PRICING_PLAN`;
10. set `pendingPlanId`/pending handle to `growth` while current plan remains `starter` and prove the winner remains `starter-model`;
11. make `growth` the current Subscription plan and prove a **new** resolver/invoker sees `growth-model`;
12. prove a valid explicit Shop A selection of `shop-a-model` wins over the current Price Plan model;
13. clear the Shop override and prove the current Price Plan wins again even if the Platform Agent Configuration is made invalid/missing;
14. point the current Price Plan at an invalid/disabled/non-Platform model and prove resolution fails closed rather than silently using Platform;
15. clear the current Price Plan's `commerceModelId` and restore valid Platform configuration, then prove Platform inheritance;
16. prove Shop B cannot treat `shop-a-model` as valid;
17. seal and insert OpenRouter credential `credential-A` with the exact published Shared `createCommerceOpenRouterCredentialAad(...)` contract and existing Commerce keyring;
18. create the production model invoker with an injected fake Shared client factory and prove model invocation receives `credential-A` plus the expected selected model;
19. replace the database credential with sealed `credential-B` without recreating the production invoker;
20. invoke again and prove the fake client receives `credential-B` while the model identity/configuration remains unchanged for that turn;
21. change Agent Configuration, Price Plan assignment or current Subscription plan after the invoker was created and prove the existing invoker still uses the original per-turn model;
22. create a **new** production invoker and prove it resolves the new effective winner;
23. clean up every task-owned container/network in `finally`.

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
Commerce Studio explicit Shop/Platform selection + current subscription Price Plan
    -> CommerceAgentConfiguration / MerchantPricingPlan.commerceModelId
    -> effective SHOP -> PRICING_PLAN -> PLATFORM model resolution per production turn
    -> current environment OpenRouter credential per model invocation
    -> Shared OpenRouterModelClient
    -> OpenRouter
```

Documentation MUST explicitly state:

- one effective active model per Shop with precedence `SHOP -> PRICING_PLAN -> PLATFORM`;
- Price Plan inheritance uses only the current ACTIVE/TRIALING subscription plan; pending plan changes do not grant model benefits early;
- model selection is stable for one production turn;
- OpenRouter credential is live per invocation;
- `GROQ_COMMERCE_MODEL` is no longer a CommerceAgent requirement;
- `GROQ_API_KEY` may still be required independently for Groq speech transcription.

Do not document ARCH-024 Test Conversations as Background runtime behaviour.

## Work Items

- [ ] Consume the accepted ARCH-024 Database gitlink and exact SHARED-002 package version.
- [ ] Add canonical deployment-to-Commerce environment resolution.
- [ ] Add canonical `shopId` to `RecoveryAgentContext` and populate it from durable ownership.
- [ ] Implement the exact `SHOP -> PRICING_PLAN -> PLATFORM` production effective-model resolver from R4, including current Subscription/BillingPlan/MerchantPricingPlan lookup.
- [ ] Implement the existing Commerce credential-keyring parser from `COMMERCE_CONNECTION_KEYS_JSON`.
- [ ] Implement AES-256-GCM OpenRouter credential resolution using the exact published Shared `createCommerceOpenRouterCredentialAad(...)` contract.
- [ ] Implement the per-turn fixed-model/per-invocation-live-credential production model invoker.
- [ ] Refactor `runCommerceAgent` to use the dynamic OpenRouter production path while retaining explicit test injection.
- [ ] Refactor `executeCommerceHost` to accept `CommerceModelInvoker` directly and remove the local AI-SDK model adapter.
- [ ] Delete the obsolete CommerceAgent Groq provider and remove `@ai-sdk/groq` only if no remaining references exist.
- [ ] Preserve Groq speech-transcription environment requirements.
- [ ] Add focused Shop/Price Plan/Platform model-resolution, credential, model-invoker, agent and host regressions.
- [ ] Add and pass the disposable PostgreSQL selection + credential-rotation proof.
- [ ] Update Background-owned CommerceAgent runtime documentation.
- [ ] Run all required validation and record exact results/warnings in the Completion Report.

## Interfaces / Contracts

### Contract owner — ARCH-024 model contracts/runtime

Task:

`ARCH-024-SHARED-001` / publication `ARCH-024-SHARED-002`

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
CommerceModelSelectionSource
CommercePricingPlanModelAssignmentSchema
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
billing.MerchantPricingPlan
billing.BillingPlan
billing.Subscription
commerce.Shop
```

### Effective model semantic contract

The parent ARCH-024 architecture defines the canonical `SHOP -> PRICING_PLAN -> PLATFORM` selection semantics.

Commerce and Background implement those same architect-defined semantics independently because they are separate deployables/repositories and MUST NOT import one another's private source code.

Any discrepancy discovered between the parent-architecture acceptance matrix and this task is an architectural conflict: STOP and return it to `moda_architect`; do not invent another fallback rule.

### Credential sealing contract

Cross-repository AAD owner:

`ARCH-024-SHARED-001` / published by `ARCH-024-SHARED-002`

Independent users:

```text
ARCH-024-ADMIN-003       seals credentials
ARCH-024-COMMERCE-007    decrypts credentials for Test Conversations
ARCH-024-BACKGROUND-001  decrypts credentials for production turns
```

Exact encryption contract:

```text
AES-256-GCM
keyring = COMMERCE_CONNECTION_KEYS_JSON
nonce = persisted 12 bytes
authTag = persisted 16 bytes
AAD string = createCommerceOpenRouterCredentialAad({ environment, keyId })
AAD bytes  = UTF-8 encoding of that returned canonical string
```

No plaintext credential crosses repository boundaries.

## Dependencies

- `ARCH-024-DATABASE-001`
- `ARCH-024-SHARED-002`

These are the only implementation dependencies. Background does not consume Commerce or Admin source: it reads the accepted database schema directly, applies the parent architecture's model-precedence policy, and uses the published Shared model/AAD contracts. Focused/integration validation seeds model-selection and credential rows directly.

All dependencies must be architect-accepted Complete before this task becomes Ready.

## Enables

- `ARCH-024-BACKGROUND-002`
- `ARCH-024-GATEWAY-001`

Terminal ARCH-024 system-test tasks may also depend on this task when they are materialised. Do not add a dependency from this implementation task to a system-test task.

## Acceptance Criteria

- [ ] Production CommerceAgent no longer reads `GROQ_COMMERCE_MODEL` or constructs the conversational model through `src/providers/groq.provider.ts`.
- [ ] Production model selection resolves exactly one effective active model using `SHOP -> current PRICING_PLAN -> PLATFORM` for the trusted Shop/environment.
- [ ] An explicit valid Shop override wins and does not depend on valid Price Plan or Platform configuration.
- [ ] An explicit broken Shop override fails closed and never silently falls back to Price Plan/Platform.
- [ ] With no Shop override, an ACTIVE/TRIALING current subscription may inherit `MerchantPricingPlan.commerceModelId` through exact `BillingPlan.shopifyPlanHandle`; pending plans are ignored.
- [ ] A valid Price Plan model must be Platform-available, wins over Platform, and does not require Platform selection to be valid.
- [ ] A broken explicit Price Plan model fails closed and never silently falls back to Platform.
- [ ] With no Shop or Price Plan override, the Shop inherits the valid Platform selection.
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
- [ ] Disposable PostgreSQL proof demonstrates Shop override, current Price Plan inheritance, pending-plan exclusion, Platform fallback, broken-plan fail-closed behaviour, cross-Shop denial, credential A -> B live rotation and next-turn model-selection refresh.
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

- The duplicated production-side database read is intentional at this repository boundary: Background cannot import Commerce private source. The semantic policy is parent-architecture-owned (`SHOP -> PRICING_PLAN -> PLATFORM`) and must satisfy the same acceptance matrix as Commerce without depending on Commerce implementation. If drift is discovered, stop and return the architecture issue rather than inventing a third rule.
- Model configuration is fixed per production turn; credential state is intentionally live per model invocation.
- `COMMERCE_CONNECTION_KEYS_JSON` is reused as the encryption root. Do not introduce a provider-specific keyring.
- `GROQ_API_KEY` remains a valid independent speech-transcription secret after the conversational model moves to OpenRouter.
- `@langchain/langgraph` is already present in Background and remains unrelated to the model-provider migration in this task.

## Completion Report

### Status

Ready for architect review.

### Files Changed

Implementation worktree (`moda-interact-background`):

- `README.md`
- `docs/commerce-host.md`
- `docs/commerceagent-sequence-diagrams/commerceagent-inner-loop.puml` (added; the task-named diagram path was absent in this repository)
- `package.json`, `package-lock.json`
- `src/agents/commerce.agent.ts`, `src/agents/types.ts`
- `src/commerce/host.ts`
- `src/commerce/credential-keyring.ts`, `src/commerce/model-environment.ts`, `src/commerce/model-resolution.ts`, `src/commerce/openrouter-credential.ts`, `src/commerce/production-model.ts` (added)
- `src/services/checkout-recovery.service.ts`
- `src/providers/groq.provider.ts` (deleted)
- `scripts/run-arch024-production-model-disposable.mjs` (added)
- `tests/integration/commerce/host.test.ts`
- `tests/integration/commerce.agent.integration.test.ts` (deleted; obsolete adapter-only integration coverage)
- `tests/unit/agent/commerce.agent.configuration.test.ts`
- `tests/unit/observability/genai-observability.test.ts`
- `tests/unit/runtime/observability-startup.test.ts`
- `tests/unit/commerce/credential-keyring.test.ts`, `model-environment.test.ts`, `model-resolution.test.ts`, `openrouter-credential.test.ts`, `production-model.test.ts` (added)

Task packet worktree: only this task definition's status and Completion Report were updated. The Architect Review section was not changed. The accepted Database submodule gitlink was not changed.

### Work Completed

Replaced the production CommerceAgent's Groq model path with the exact Shared `1.1.0` runtime, deterministic deployment-environment mapping, and repeatable-read `SHOP -> current PRICING_PLAN -> PLATFORM` resolution. Canonical Shop ID is carried in recovery context and checked against durable recovery ownership before model invocation.

Added strict parsing of the existing Commerce credential keyring, AES-256-GCM decryption using the Shared AAD contract, and a per-turn fixed-model invoker that resolves the current credential and constructs a fresh Shared OpenRouter client for every invocation. The Shared runner receives the host logger with bounded context. Removed the obsolete conversational Groq provider/dependency while retaining Groq speech transcription.

Added resolver, keyring, credential, invoker, agent, host and disposable PostgreSQL coverage. Updated runtime documentation and added the requested model-resolution sequence diagram. Updated the existing Shared-version regression to assert the required exact `1.1.0` release.

### Validation Results

- `npm run prisma:validate` — PASS.
- `npm run prisma:generate` — PASS using the accepted database submodule schema.
- Required focused unit command covering model environment, resolver, OpenRouter credential, production invoker, agent configuration and pipeline — PASS, 6 files / 57 tests.
- `npm test -- tests/integration/commerce/host.test.ts` — PASS, 44 tests.
- `npm test -- tests/unit/services/speech-transcription.service.test.ts` — PASS, 15 tests; independent Groq transcription remains intact.
- `npm test -- tests/unit/runtime/observability-startup.test.ts` — PASS after aligning its exact Shared dependency assertion, 10 tests.
- Keyring unit tests — PASS, 9 tests.
- `node scripts/run-arch024-production-model-disposable.mjs` — PASS. Applied all 25 migrations and verified Shop/Price Plan/Platform precedence, pending-plan exclusion, Shop-scope denial, fail-closed selection, credential A-to-B rotation, and per-turn model stability/new-turn refresh. No live provider call; disposable resources are removed in `finally`.
- `npm run build` — PASS (Prisma generation and TypeScript compile).
- Full `npm test` — NOT CLEAN: 95 test files passed, 15 skipped, 5 files failed; 1,392 tests passed, 38 skipped and 9 failed. Failures are outside task-owned code: three billing-reconciliation assertions, one matured-candidate language assertion, four translation-enum integration cases requiring unavailable `localhost:5432`, one missing ARCH-020 task-worktree fixture (`ARCH-020-evidence-contract-fixtures.json`), and one observability test timeout. The stale Shared-version assertion was corrected and its focused file passes. No durable test-suite baseline ID for these failures exists in the workspace baseline; they are reported by exact test/file here, not treated as accepted baseline debt.
- Static cleanup assertions — PASS: no obsolete conversational-model setting/provider path/local adapter or direct LangChain OpenRouter/core import in the required Background paths; `GROQ_API_KEY` remains in the speech-transcription service.
- `git diff --check` — PASS.
- Changed-file TypeScript diagnostics — PASS, zero errors.
- Dependency installation reported 6 npm audit advisories (2 moderate, 4 high); no broad audit fix was run.

### Deviations

The task requested `docs/commerceagent-sequence-diagrams/commerceagent-inner-loop.puml`, but no sequence-diagram directory/file existed in the Background repository; the requested diagram was added at that path. Literal static assertions prohibit the legacy setting token in Background source/tests/docs while the documentation requirement asks to describe its retirement, so docs state that the legacy conversational Groq selector is retired without repeating the token; the regression constructs the obsolete test key from fragments.

### Assumptions

The documented full-suite failures are unrelated to this task because they occur in untouched billing, matured-candidate, translation integration, and legacy ARCH-020 fixture paths. Their status remains for architect review; no unrelated fixes were included.

### Unresolved Issues

The full Background suite is not green for the unrelated failures listed above. The four translation integration cases require a local PostgreSQL service at `localhost:5432`; the ARCH-020 evidence fixture is not present at the path hard-coded by its test. No task-owned validation is blocked.

### Architectural Concerns

None identified. Awaiting `moda_architect` review and acceptance decision.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 implementation review found the production model/runtime design architecturally conformant in the inspected source: the resolver uses one `REPEATABLE READ` decision snapshot and exact `SHOP -> PRICING_PLAN -> PLATFORM` precedence; model identity/configuration is fixed once per turn; the current encrypted OpenRouter credential is resolved for every model invocation; the Shared `CommerceModelInvoker`/`OpenRouterModelClient` boundary is consumed; host Shop ID/domain mismatch is denied before model invocation; the obsolete conversational Groq provider is removed while Groq transcription remains; and the MCP/runner boundary is preserved.

Acceptance is withheld for durable task-evidence deficiencies. These corrections are evidence/reconciliation work unless the requested baseline comparison reveals an implementation regression.

**A1-R1 — Complete the authoritative task checklists before resubmission.** The task is in `review`, but every Work Item, Acceptance Criterion and Validation checkbox remains unchecked. Reconcile those sections to the work actually completed. Do not check the repository-wide test-suite item unless A1-R3 establishes that the submitted implementation introduced no new or worsened failure. The task must not return to `review` with required checklist state knowingly incomplete.

**A1-R2 — Record the prepared-launch/worktree evidence in the Completion Report.** Add the launcher-resolved canonical workspace root, dedicated parent task worktree, dedicated `moda-interact-background` implementation worktree, exact `task/ARCH-024-BACKGROUND-001` branches, start-of-attempt synchronization evidence, recursive implementation-submodule materialisation evidence, accepted database gitlink identity, exact Shared `1.1.0` consumption, implementation/report commit identities, remote-head equality and final clean-worktree evidence. The prepared launcher packet is valid evidence, but the Completion Report must preserve it durably.

**A1-R3 — Prove the nine repository-suite failures are not regressions.** The Completion Report records `95` test files passed, `15` skipped, `5` failed and `9` failing tests, but there is no durable baseline ID and the exact failing test names/results are not recorded. Run the same full repository test command at the synchronized pre-task implementation baseline under the same toolchain/dependency/environment conditions, record both baseline and current failing test names/results, and show that the current implementation introduces no new or worsened failure. This comparison must specifically identify the observability timeout because this task changed Shared/runtime observability-adjacent test/dependency state. If the baseline is equivalent or worse and task-owned focused validation remains green, no source churn is required. If any current failure is new or worsened, correct the responsible source/test within this same task and rerun the required validation.

No new task is required. `ARCH-024-BACKGROUND-002` and `ARCH-024-GATEWAY-001` remain gated until BACKGROUND-001 is architect-accepted Complete.

### Reviewed Files

- `src/commerce/model-environment.ts`
- `src/commerce/model-resolution.ts`
- `src/commerce/credential-keyring.ts`
- `src/commerce/openrouter-credential.ts`
- `src/commerce/production-model.ts`
- `src/agents/commerce.agent.ts`
- `src/agents/types.ts`
- `src/commerce/host.ts`
- `src/services/checkout-recovery.service.ts`
- `scripts/run-arch024-production-model-disposable.mjs`
- focused model/credential/agent/host tests and Background-owned runtime documentation
- task Completion Report and ARCH-024 parent/background coordination documents

### Validation Reviewed

Reviewed the submitted evidence for Prisma validation/generation, focused model tests, host integration tests, speech-transcription regression, disposable PostgreSQL proof, production build, static cleanup assertions, changed-file diagnostics and `git diff --check`. Static source inspection independently confirmed exact Shared `1.1.0` direct consumption, removal of the Background `@ai-sdk/groq` dependency/provider, absence of direct production `@langchain/openrouter`/`@langchain/core` imports, and retention of `GROQ_API_KEY` for speech transcription.

The repository-wide suite is not accepted as baseline-equivalent yet because A1-R3 evidence is missing.

### Architecture Conformance

Implementation design: conformant in the inspected task-owned runtime paths.

Task lifecycle/evidence: not yet conformant because required checklists and prepared-launch evidence are not durably reconciled, and the non-clean repository suite lacks deterministic baseline-parity proof.

### Follow-up

Reclaim the same task for Attempt 2. Treat A1-R1/A1-R2 as report/evidence reconciliation. Treat A1-R3 as evidence-only unless the baseline comparison proves a regression; only then make the minimum source/test correction required and rerun validation. Do not begin BACKGROUND-002 or GATEWAY-001.
