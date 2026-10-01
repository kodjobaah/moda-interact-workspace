---
id: ARCH-024-COMMERCE-006
architecture_id: ARCH-024
title: Execute Test Conversation Tools against the selected shop
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
  - ARCH-024-COMMERCE-005
enables:
  - ARCH-024-COMMERCE-007
created: 2026-09-30
updated: 2026-09-30
---

# Execute Test Conversation Tools against the selected shop

## Architecture

Architecture ID:

`ARCH-024`

Architecture document:

`docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`

Coordinator:

`moda_architect`

## Objective

Replace the retained synthetic/fixture Tool executor for **Feature-composed Test Conversations** with the existing production `DefinitionExecutor` and the exact selected Shop context established by ARCH-024-COMMERCE-005.

The target execution boundary is:

```text
Conversation Configuration Snapshot
    selected Shop id/domain
    exact Tool revision definitions
    exact Feature-composed grant/manifest
            |
            v
Commerce runner requests one granted Tool
            |
            v
Preview conversation Tool executor
            |
            v
existing production DefinitionExecutor
      /             |              \
     /              |               \
Shopify Admin   Policy Operation   External HTTP
     |              |               |
current offline  selected Shop   current connection
Shopify session   runtime state   + current credential
```

The task MUST NOT create fixture Shopify facts, fixture External HTTP responses, fake connection credentials, or fabricated durable CheckoutRecovery/customer state for the human Test Conversation path.

The Test Conversation continues to be an isolated **staff preview**: Tool execution may perform the same bounded provider reads/evaluations as the existing published Tool executor, but this task MUST NOT introduce customer messaging, CheckoutRecovery mutation, order mutation, discount mutation, or any other new side-effecting operation.

This task wires real Tool execution only. The human message composer remains disabled until ARCH-024-COMMERCE-007 installs the OpenRouter model runtime and enables complete conversation turns.

## Context

ARCH-024-COMMERCE-004 changes human Test Conversation composition to selected Features and stores exact published Tool revisions in the server-side conversation snapshot.

ARCH-024-COMMERCE-005 changes conversation start to require a validated selected Shop and carries that Shop identity into the Feature-composed conversation grant. It deliberately leaves actual conversation execution disabled until the remaining runtime tasks are complete.

The current pre-ARCH-024 Preview adapter still executes conversation Tools through:

```text
backend.createFixtureExecution(...)
fixtureQuery(...)
shopDomain = preview.myshopify.com
shopId = preview-<admin>
```

That implementation is not valid for the replacement Test Conversation experience.

The production Commerce backend already owns the execution machinery this task must reuse:

```text
CommerceBackend.execution
    -> DefinitionExecutor
       -> production Shopify Admin query port
       -> production PolicyOperation registry
       -> production External HTTP execution port
```

The production Shopify Admin query port obtains the current offline session token from the current Shop domain at execution time. The External HTTP execution port resolves the current configured connection/credential at execution time. Policy Operations receive the current `AuthorizedToolCall` Shop identity and use their existing production adapters.

Do not introduce a second Tool execution implementation for Test Conversations.

## Scope

Primary implementation targets:

```text
moda-interact-commerce/src/commerce/preview/types.ts
moda-interact-commerce/src/commerce/preview/service.ts
moda-interact-commerce/src/commerce/integration/preview/adapters.ts
moda-interact-commerce/lib/preview/runtime.ts

moda-interact-commerce/src/commerce/connections/credentials/index.ts   # only R11 runtime-scope correction

moda-interact-commerce/tests/preview-integration.test.ts
moda-interact-commerce/tests/preview-service.test.ts
moda-interact-commerce/tests/definition-execution.test.ts             # only when needed for real Preview call construction
```

Create one focused test file at exactly:

```text
moda-interact-commerce/tests/selected-shop-preview-tool-execution.test.ts
```

for the selected-Shop matrix in R13.

If the accepted ARCH-024-COMMERCE-005 implementation places the selected-Shop server resolver in an additional Preview route/helper file, that exact file may be changed only to carry the bounded server-resolved Shop execution context defined in R1/R2. Record it in the Completion Report.

Additional Commerce files may change only when mechanically required to wire the exact contracts below. Every additional file MUST be listed and justified in the Completion Report.

Do not modify:

```text
moda-interact-commerce/database/**
moda-interact-shared/**
moda-interact-admin/**
moda-interact-background/**
moda-interact-gateway/**
```

## Out of Scope

- OpenRouter/LangChain model invocation; ARCH-024-COMMERCE-007 owns it.
- Enabling the Test Conversation message composer; ARCH-024-COMMERCE-007 owns it.
- Changing the active Commerce model.
- Model Catalogue / Model Availability administration.
- OpenRouter credential lookup/decryption.
- Changing Feature composition semantics from ARCH-024-COMMERCE-004.
- Per-Capability selection/exclusion.
- Creating/publishing Tools or Releases.
- Customer/merchant-facing messaging.
- Creating fake CheckoutRecovery, Customer, Order, Discount or other durable business rows for Preview.
- Adding Tool mutations that do not already exist in the accepted production `DefinitionExecutor` path.
- Removing fixture-backed **Tool Authoring / Code Response** tests or `/api/studio/preview/tool-tests`.
- Removing fixture helpers still required by those independent Tool-test paths.
- Removing `COMMERCE_PREVIEW_PROVIDER`, `COMMERCE_PREVIEW_MODEL` or `COMMERCE_PREVIEW_API_KEY`; the OpenRouter/Gateway cutover owns that later.
- LangGraph adoption.
- Database or Shared-package changes.

## Requirements

### R1 — persist one server-resolved Shop execution identity with the conversation

The browser start request from ARCH-024-COMMERCE-005 remains exactly:

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

The browser MUST NOT send `shopDomain`.

After the server-side Shop revalidation already required by ARCH-024-COMMERCE-005, persist exactly this non-secret execution identity in the server-side Preview conversation state:

```ts
export const PreviewConversationShopSchema = z.strictObject({
  id: SavedIdSchema,
  domain: z.string().trim().min(1).max(255),
});

export type PreviewConversationShop = z.infer<typeof PreviewConversationShopSchema>;
```

Add to `StoredConversation`:

```ts
shop: PreviewConversationShop;
```

and to `StoredConversationSchema`:

```ts
shop: PreviewConversationShopSchema,
```

The persisted Shop MUST be constructed only from the accepted server-side Shop resolution result. Never copy a domain from URL/query/body data.

`StoredConversation.shop.id` MUST equal:

```text
StoredConversation.bundle.grant.shopId
```

or conversation creation MUST fail as `UNAVAILABLE`.

ARCH-024 is pre-production. Existing development Preview records without `shop` may be discarded/flushed. Do not add backwards-compatible parsing for them.

### R2 — snapshot Shop id/domain, keep credentials live

For one started Test Conversation:

```text
Shop id/domain
    -> Conversation Configuration Snapshot
    -> stable until Start new conversation
```

This task intentionally snapshots the selected Shop identity/domain used to construct Tool calls.

Do **not** snapshot:

```text
Shopify access token / Session row
External HTTP credential plaintext/ciphertext
External connection resolved authentication headers
Policy-operation provider responses
```

Those operational dependencies remain live and are resolved by the existing production execution dependencies when each Tool call occurs.

Therefore a Shopify/External credential rotation after conversation start MUST be observable by the next Tool invocation without recreating the conversation.

### R3 — split human-conversation Tool execution from retained fixture Tool testing

Do not continue using one fixture-shaped `PreviewToolExecutionPort` for both human conversations and independent Tool tests.

In `src/commerce/preview/types.ts`, introduce exactly:

```ts
export interface PreviewConversationToolExecutionPort {
  execute(input: {
    descriptor: ToolDescriptor;
    arguments: Record<string, unknown>;
    signal: AbortSignal;
    environment: string;
    bundle: PreviewBundle;
    snapshot: PreviewFrozenSnapshot;
    shop: PreviewConversationShop;
    conversationId: string;
  }): Promise<CommerceToolResult>;
}
```

Retain the fixture-backed Tool-test port used by `runToolTest(...)`. It may keep its current name if the accepted C001/C005 implementation has already separated the human path, otherwise rename it deterministically to:

```ts
export interface PreviewFixtureToolTestExecutionPort {
  load(input: {
    principal: PreviewPrincipal;
    toolRevisionId: string;
    fixture: PreviewFixture;
  }): Promise<FrozenFixtureTool>;
}
```

and update only its independent Tool-test consumers.

`PreviewServiceDependencies` MUST contain separate dependencies:

```ts
conversationToolExecutor?: PreviewConversationToolExecutionPort;
fixtureToolTestExecutor?: PreviewFixtureToolTestExecutionPort;
```

If C001/C005 already established equivalent names, preserve those accepted names rather than adding aliases; the architectural invariant is **two distinct ports**, one real selected-Shop conversation executor and one retained fixture Tool-test executor.

### R4 — implement one selected-Shop conversation executor using `CommerceBackend.execution`

In `src/commerce/integration/preview/adapters.ts`, create exactly one factory:

```ts
export function createSelectedShopPreviewToolExecutor(
  backend: CommerceBackend,
  environment: string,
): PreviewConversationToolExecutionPort
```

The implementation MUST execute through:

```ts
backend.execution.execute(...)
```

which is the production `DefinitionExecutor` already configured by `getCommerceBackend()`.

It MUST NOT call:

```text
backend.createFixtureExecution(...)
fixtureQuery(...)
createDefinitionExecutor(...) with Preview-only dependencies
```

for Feature-composed human Test Conversations.

### R5 — use only the exact frozen Tool definition

For every conversation Tool execution:

1. find exactly one frozen definition in:

```ts
snapshot.definitions
```

where:

```text
revisionId = descriptor.toolRevisionId
```

2. parse it through `CommerceToolDefinitionSchema`;
3. fail closed if the frozen definition is absent/invalid;
4. do not reread the current `CommerceToolRevision.definition` from PostgreSQL;
5. do not substitute a newer published Tool revision.

This preserves the Conversation Configuration Snapshot semantics from ARCH-024-COMMERCE-004.

Required failure result for missing/invalid frozen definition:

```ts
{
  contractVersion: 'commerce.v1',
  status: 'ERROR',
  code: 'INCOMPATIBLE_VERSION',
  retryable: false,
}
```

### R6 — revalidate descriptor/grant/snapshot integrity before execution

Before calling `backend.execution.execute(...)`, the selected-Shop executor MUST prove all of these:

```text
bundle.grant.shopId === shop.id
bundle.grant.conversationId === conversationId

descriptor appears in bundle.manifest.capabilities
    by exact toolId + toolRevisionId

matching bundle.grant.grantedTools entry exists
    with exact toolId + toolRevisionId + toolName + definitionVersion

frozen definition.name === descriptor.name
frozen definition.definitionVersion === descriptor.definitionVersion
frozen definition.description === descriptor.description
canonical frozen definition.inputSchema === canonical descriptor.inputSchema
```

Use the existing Shared/local canonical JSON helper already used by the MCP runtime rather than inventing a second structural comparator.

Any mismatch MUST return bounded:

```text
INCOMPATIBLE_VERSION
```

and MUST NOT dispatch a provider request.

### R7 — construct one exact `AuthorizedToolCall`

After R5/R6 pass, call `backend.execution.execute(...)` with:

```ts
{
  turn: {
    contractVersion: 'commerce.v1',
    shopId: shop.id,
    checkoutRecoveryId: `preview-${conversationId}`,
    conversationId,
    inboundVersion: bundle.grant.initialInboundVersion,
  },
  grantId: bundle.grant.id,
  releaseId: bundle.grant.releaseId,
  toolId: descriptor.toolId,
  toolRevisionId: descriptor.toolRevisionId,
  name: descriptor.name,
  definition,
  arguments,
  shopDomain: shop.domain,
  environment: parsedEnvironment,
  limits: {
    maxPolicyOutputItems: 3,
    maxCollectionItems: 20,
  },
  deadlineAt,
  signal: boundedSignal,
  budget,
  purpose: 'preview',
}
```

`parsedEnvironment` MUST use the existing Commerce `Environment` validation/type rather than `as never`/unchecked casting.

`checkoutRecoveryId = preview-<conversation UUID>` is an execution identity only. **Do not create a CheckoutRecovery row with that ID.** Policy Operations that require a real recovery/customer/order context must return their existing bounded NOT_FOUND/UNAVAILABLE/DENIED result instead of receiving fabricated state.

### R8 — match the existing production per-Tool execution budget

The selected-Shop Preview Tool executor MUST use the same provider-attempt/deadline envelope as the existing MCP `tools/call` execution path:

```text
Tool deadline                10,000 ms
Maximum provider reservations       12
```

Implement the budget semantics exactly:

```ts
let providerRequests = 0;

const budget = {
  reserveProviderRequest() {
    if (
      boundedSignal.aborted ||
      now() >= deadlineAt ||
      providerRequests >= 12
    ) {
      throw new McpError('DEADLINE', 'tool budget exhausted', 409, true);
    }
    providerRequests += 1;
  },
};
```

Use an internal `AbortController` that is aborted when either:

```text
caller signal aborts
OR
10-second deadline expires
```

Always clear timers/listeners in `finally`.

Do not raise the runner remote-call/model-step budgets in this task.

### R9 — Shopify Admin execution uses the current selected-Shop offline session

For `SHOPIFY_ADMIN_GRAPHQL`, C006 MUST use the existing production Admin query dependency already wired into `backend.execution`.

The call MUST provide:

```text
turn.shopId  = selected Shop id
shopDomain   = selected Shop domain
```

The production Admin query session provider MUST continue to resolve the current offline session/token at execution time.

Required semantics:

```text
current offline session exists
    -> execute against selected Shop

no current offline session / token unavailable
    -> bounded CommerceToolResult ERROR
       using existing DefinitionExecutor/Admin-query mapping
```

Do not pre-seed or copy the token into Preview state.

Do not fall back to fixture Shopify facts.

### R10 — Policy Operations execute with selected-Shop identity and no fabricated business state

For `POLICY_OPERATION`, use the production Policy Operation registry already wired into `backend.execution`.

The Tool call MUST expose:

```text
context.turn.shopId = selected Shop id
context.shopDomain  = selected Shop domain
context.purpose     = preview
```

Do not create fake durable:

```text
CheckoutRecovery
Customer
Order
Discount
Conversation
```

records to satisfy a Policy Operation.

A Policy Operation that requires durable state not represented by this Test Conversation must return its existing bounded error outcome.

Policy Operations that can operate from the selected-Shop context without such state may execute normally.

### R11 — External HTTP execution uses current selected-Shop connection semantics

For `EXTERNAL_HTTP`, use the production External HTTP execution dependency already wired into `backend.execution`.

The selected Shop ID MUST be the runtime Shop identity passed to connection resolution.

The existing credential resolver currently treats a non-null runtime Shop ID as invalid for a `PLATFORM` connection even though `DefinitionExecutor` always carries a Shop identity. Correct only the runtime `resolveConnection(...)` semantics in:

```text
src/commerce/connections/credentials/index.ts
```

as follows:

```ts
revision.scope === 'PLATFORM'
    -> credentialShopId = null
    -> the caller's runtime shopId does NOT make the connection forbidden

revision.scope === 'PER_SHOP'
    -> require caller shopId != null
    -> credentialShopId = caller shopId
```

Then resolve credentials using `credentialShopId`.

Do **not** change Admin credential mutation/status scope validation. Admin writes to a Platform credential with `shopId = null`; Shop credentials remain keyed by the exact Shop ID.

Required regression matrix:

```text
PLATFORM + auth NONE               -> selected-Shop Tool may execute
PLATFORM + configured credential   -> selected-Shop Tool may execute using Platform credential
PER_SHOP + exact Shop credential   -> may execute
PER_SHOP + missing credential      -> DENIED/UNAVAILABLE per existing bounded mapping
PER_SHOP + another Shop credential -> MUST NOT use it
```

No connection credential value may enter Preview state, result traces, UI props or logs.

### R12 — PreviewService conversation execution uses only the new conversation Tool port

In the conversation `RunnerTool.execute(...)` path, remove use of:

```text
fixture
externalResponseFixtures
externalResponseDefinitions
externalFixtureRunner
fixture-backed conversation tool execution
```

for Feature-composed human Test Conversations.

The path MUST call only:

```ts
conversationToolExecutor.execute({
  descriptor,
  arguments,
  signal,
  environment: this.environment,
  bundle: conversation.bundle,
  snapshot: conversation.snapshot,
  shop: conversation.shop,
  conversationId: conversation.id,
})
```

The independent `runToolTest(...)` path MUST continue using the retained fixture Tool-test executor and fixture IDs.

Do not remove `externalFixtureRunner` if it remains referenced by Code Response / Tool-test infrastructure after C001/C005. If conversation-specific references become dead, remove only those dead references and record the reference audit in the Completion Report.

### R13 — exact selected-Shop Tool execution test matrix

Create:

```text
tests/selected-shop-preview-tool-execution.test.ts
```

The test MUST exercise the selected-Shop conversation executor with a real `DefinitionExecutor` dependency seam rather than asserting only object construction.

Cover at minimum:

1. **snapshot integrity**
   - exact frozen revision executes;
   - newer current DB revision is not reread/substituted;
   - missing frozen revision -> `INCOMPATIBLE_VERSION`;
   - descriptor/definition mismatch -> `INCOMPATIBLE_VERSION` before provider dispatch.

2. **selected-Shop identity**
   - `turn.shopId` is exact selected Shop ID;
   - `shopDomain` is exact server-resolved selected Shop domain;
   - grant Shop mismatch fails closed before provider dispatch;
   - conversation ID is the persisted Preview conversation ID;
   - no `preview.myshopify.com` or `preview-<admin>` identity is used.

3. **Shopify Admin**
   - current offline token is resolved at Tool execution time;
   - selected Shop domain is used;
   - missing offline session produces bounded failure;
   - fixture query adapter is never called.

4. **Policy Operation**
   - production registry adapter receives selected Shop identity;
   - no fake CheckoutRecovery row is created;
   - missing required durable state remains bounded failure.

5. **External HTTP**
   - Platform connection executes with global credential while call retains selected Shop identity;
   - per-Shop connection executes only with exact selected Shop credential;
   - another Shop's credential is never selected;
   - current credential replacement is observed by a later execution without recreating conversation state.

6. **budget/cancellation**
   - 13th provider reservation is rejected;
   - caller abort cancels execution;
   - 10-second deadline maps to bounded deadline outcome;
   - timers/listeners are cleaned up.

No test may make a live Shopify or External network request. Use deterministic injected transports/session/credential dependencies.

### R14 — Preview integration tests prove conversation/Tool-test separation

Update existing Preview service/integration tests to prove:

```text
Feature Test Conversation Tool call
    -> conversationToolExecutor only
    -> no fixture executor

independent /api/studio/preview/tool-tests
    -> fixtureToolTestExecutor still works
    -> fixture behaviour unchanged
```

Also prove that Feature Test Conversation start/run state contains no:

```text
fixtureId
externalResponseFixtures
externalResponseDefinitions
Shopify access token
External authentication header
```

if those fields have become conversation-dead after accepted C001/C005 work.

If retained Store schemas still require fixture-only fields for `StoredToolTest`, keep them there; do not force unrelated Tool tests onto the human conversation shape.

### R15 — do not enable human model turns yet

C006 MUST NOT remove the C005 transitional message-composer lock.

The human Test Conversations screen must still display:

```text
Conversation execution is enabled by the remaining ARCH-024 runtime tasks.
```

with disabled message textarea / Send controls after C006.

Tests MUST prove C006 does not accidentally re-enable the old fixture/model conversation execution path.

ARCH-024-COMMERCE-007 is the task that installs OpenRouter execution and enables complete Test Conversation turns.

### R16 — secret and telemetry safety

No log, trace, Preview result, Redis conversation state or browser response added/changed by this task may contain:

```text
Shopify access token
External HTTP credential plaintext
External authentication header values
External credential ciphertext/nonce/authTag/keyId
session body
provider response body beyond existing bounded Tool result contract
```

Telemetry may include only existing bounded identifiers/outcomes such as:

```text
environment
purpose = preview
Tool revision ID
request/run ID
bounded outcome/provider-attempt count
```

Do not add Shop access tokens, connection secrets, Tool arguments or full provider payloads as telemetry attributes.

### R17 — no new persistence outside Preview state

Running a Feature-composed Test Conversation Tool MUST NOT write new durable business data merely to make Preview succeed.

This task MUST NOT add writes to:

```text
Shop
Session
CheckoutRecovery
Customer
Order
Feature
CommerceCapability
CommerceTool / CommerceToolRevision
CommerceRelease / pointer
CommerceAgentConfiguration
CommerceExternalConnection / Revision / Credential
Merchant Knowledge source/chunk state
Billing/subscription state
```

Normal provider reads and existing non-mutating runtime evaluation are allowed.

## Work Items

- [ ] Add `PreviewConversationShopSchema` / `PreviewConversationShop` and persist the server-resolved Shop identity in `StoredConversation`.
- [ ] Split human conversation Tool execution from retained fixture Tool-test execution.
- [ ] Add `PreviewConversationToolExecutionPort` with the exact R3 contract.
- [ ] Implement `createSelectedShopPreviewToolExecutor(...)` using `backend.execution` only.
- [ ] Enforce frozen-definition and descriptor/grant integrity before provider dispatch.
- [ ] Construct the exact selected-Shop `AuthorizedToolCall` from R7.
- [ ] Apply the production-equivalent 10-second / 12-provider-request Tool budget.
- [ ] Route Shopify Admin execution through the current selected-Shop offline session.
- [ ] Route Policy Operations through the production registry without fabricated durable business state.
- [ ] Correct runtime Platform/per-Shop External credential resolution per R11.
- [ ] Route External HTTP execution through the production connection/credential machinery.
- [ ] Update PreviewService conversation Tool execution to use only the selected-Shop executor.
- [ ] Preserve independent fixture-backed Tool Authoring / Code Response Tool tests.
- [ ] Add the full selected-Shop Tool execution regression matrix.
- [ ] Keep human message execution disabled until C007.
- [ ] Validate secret/telemetry/persistence safety.

## Interfaces / Contracts

### Consumes

From ARCH-024-COMMERCE-004/005:

```text
PreviewSelection = FEATURES
Feature-composed PreviewBundle / grant
PreviewFrozenSnapshot exact Tool definitions
selected Shop id carried into grant
validated server-side Shop resolution
```

Existing Commerce runtime:

```ts
CommerceBackend.execution
DefinitionExecutor
AuthorizedToolCall
CommerceToolResult
CommerceToolDefinitionSchema
```

Production execution dependencies already installed in `getCommerceBackend()`:

```text
AdminQueryExecutionPort
PolicyOperationRegistry
ExternalHttpExecutionPort
```

### Produces

```ts
PreviewConversationShopSchema
PreviewConversationShop
PreviewConversationToolExecutionPort
createSelectedShopPreviewToolExecutor(...)
```

and a Feature Test Conversation execution path in which all Tool calls use the real selected Shop context.

### Does not produce/change

```text
model runtime contract
OpenRouter credential contract
Feature composition contract
Agent Configuration contract
Shared package schemas
```

## Dependencies

- `ARCH-024-COMMERCE-005`

No Database/Shared/Admin dependency is added directly here because this task reuses the accepted Commerce production Tool executor and the selected-Shop Feature conversation established by C005.

## Enables

- `ARCH-024-COMMERCE-007`

## Acceptance Criteria

- [ ] Human Feature Test Conversations no longer execute Shopify/Policy/External Tools through fixture execution.
- [ ] The selected Shop ID and server-resolved domain are persisted server-side with the conversation and never accepted from browser domain input.
- [ ] `bundle.grant.shopId` must equal the persisted selected Shop ID.
- [ ] Conversation Tool execution uses `backend.execution` / the existing production `DefinitionExecutor`.
- [ ] Exact frozen Tool revision definitions are used; later Tool publication does not alter a started conversation.
- [ ] Descriptor/grant/snapshot mismatch fails closed before any provider request.
- [ ] Shopify Admin Tools resolve the current selected-Shop offline session/token at Tool execution time.
- [ ] Missing Shopify offline session produces bounded failure and never falls back to fixture facts.
- [ ] Policy Operations receive the selected Shop identity and no fake durable recovery/customer/order state is created.
- [ ] Platform External connections work with their global credential while the Tool call retains selected-Shop identity.
- [ ] Per-Shop External connections can use only the exact selected Shop credential.
- [ ] Credential rotation is observed by the next Tool invocation without recreating the Test Conversation.
- [ ] Selected-Shop Tool execution uses a 10-second deadline and at most 12 provider reservations.
- [ ] Caller cancellation propagates to provider execution.
- [ ] `/api/studio/preview/tool-tests` and its retained fixture executor remain functional and separate.
- [ ] The human Test Conversation message composer remains disabled after C006.
- [ ] No Shopify/External secret is persisted into Preview conversation state, returned to the browser or added to telemetry.
- [ ] No new durable business-state mutation is introduced by Test Conversation Tool execution.

## Validation

Before running Node commands, follow the workspace Node bootstrap policy.

Inspect `package.json` before running repository commands; do not invent missing scripts.

Required validation:

- [ ] Focused tests including at minimum:

```text
tests/selected-shop-preview-tool-execution.test.ts
tests/preview-service.test.ts
tests/preview-integration.test.ts
tests/external-http-executor.test.ts or the accepted equivalent credential/external execution regression suite
```

- [ ] Existing DefinitionExecutor tests covering Shopify Admin / Policy / External remain green.
- [ ] Existing Tool Authoring / Code Response fixture Tool-test tests remain green.
- [ ] Same-tick/cancellation/unknown Preview service tests affected by the port split remain green.
- [ ] TypeScript typecheck using the repository-declared command.
- [ ] Targeted ESLint for every changed TS/TSX file using the repository-declared lint capability.
- [ ] Production build using the repository-declared build command.
- [ ] Changed-file diagnostics contain no new errors.
- [ ] `git diff --check`.
- [ ] Static search proves the human conversation path no longer references `preview.myshopify.com`, `fixtureQuery(...)` or `backend.createFixtureExecution(...)`.
- [ ] Static search proves retained `/api/studio/preview/tool-tests` still has its fixture-backed implementation.
- [ ] Static/fixture inspection proves no secret-bearing field was added to `StoredConversation`, Preview result contracts, logs or browser props.

Live Shopify/OpenRouter/External network calls are NOT required for this repository task. Deterministic injected integration tests are the required proof.

If a required repository command is blocked by a documented baseline condition, record the baseline ID and prove no changed file introduces a new failure according to the architect protocol.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

1. complete the Completion Report;
2. set task status to `review`;
3. clear no architect-owned coordination state;
4. return control to `moda_architect`;
5. **STOP**.

Do not begin ARCH-024-COMMERCE-007 or any adjacent OpenRouter/model-runtime work.

## Implementation Notes

- This task deliberately reuses `CommerceBackend.execution`. Do not build a Preview-specific Shopify/Policy/External executor.
- Snapshot **configuration identity**, not credentials. The exact Tool definition and selected Shop id/domain are stable for a started Test Conversation; Shopify/External credentials remain live.
- `purpose: 'preview'` is required on `AuthorizedToolCall` so Preview execution remains distinguishable in telemetry/domain adapters.
- `checkoutRecoveryId = preview-<conversationId>` is only a bounded execution identity. It MUST NOT be persisted as a real CheckoutRecovery.
- The R11 Platform-connection correction is authorised because the existing production `ExternalHttpExecutionPort` always executes in a Shop turn, while Platform credentials are globally scoped. Do not broaden the correction into credential-administration redesign.
- C006 intentionally leaves the human message composer disabled. This allows real Tool-execution wiring to be reviewed independently before OpenRouter/model execution is enabled.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run.

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

Pending.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Follow-up

Pending.
