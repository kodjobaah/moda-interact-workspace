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
status: review
priority: 50
executor: copilot
claimed_at: 2026-10-02T00:34:11Z
attempt: 2
depends_on:
  - ARCH-024-COMMERCE-005
enables:
  - ARCH-024-COMMERCE-007
created: 2026-09-30
updated: 2026-10-02
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

ARCH-024-COMMERCE-005 changes conversation start to require a validated selected Shop and atomically freezes the complete `PreviewConversationSnapshot`, including Shop id/domain, model/instructions and the C004 Feature composition. It deliberately leaves actual conversation execution disabled until the remaining runtime tasks are complete.

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

The accepted ARCH-024-COMMERCE-005 Start path and snapshot construction are read-only dependencies of this task. Do not change conversation-start authored-state resolution merely to wire Tool execution.

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

### R1 — consume the exact C005 Conversation Configuration Snapshot without extending it

The browser start request remains exactly the C005 contract:

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

C005 already persists the authoritative selected-Shop execution identity at:

```text
conversation.snapshot.shop.id
conversation.snapshot.shop.domain
```

This task MUST NOT introduce:

```text
StoredConversation.shop
another Shop snapshot
another model/instruction snapshot
another authored-state object
```

Before any Tool execution, require:

```text
conversation.snapshot parses as PreviewConversationSnapshot
conversation.snapshot.shop.id === conversation.bundle.grant.shopId
```

Any mismatch is bounded `INCOMPATIBLE_VERSION`/`UNAVAILABLE` according to the existing Preview/runner boundary and MUST occur before a provider request.

ARCH-024 is pre-production. Existing development Preview records without the C005 complete snapshot may be discarded/flushed. Do not add backwards-compatible parsing.

### R2 — Shop/model/instruction authoring stays frozen; operational credentials stay live

For one started Test Conversation, C006 consumes but never modifies:

```text
snapshot.shop
snapshot.model
snapshot.instructions
snapshot.definitions
snapshot.prompts
bundle.manifest/grant
```

This task intentionally uses the frozen `snapshot.shop.id/domain` to construct Tool calls.

Do **not** snapshot or cache:

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
    snapshot: PreviewConversationSnapshot;
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
bundle.grant.shopId === snapshot.shop.id
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
    shopId: snapshot.shop.id,
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
  shopDomain: snapshot.shop.domain,
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
turn.shopId  = snapshot.shop.id
shopDomain   = snapshot.shop.domain
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
context.turn.shopId = snapshot.shop.id
context.shopDomain  = snapshot.shop.domain
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

- [x] Consume and validate the C005 `PreviewConversationSnapshot`; do not add another Shop/authored-state field to `StoredConversation`.
- [x] Split human conversation Tool execution from retained fixture Tool-test execution.
- [x] Add `PreviewConversationToolExecutionPort` with the exact R3 contract.
- [x] Implement `createSelectedShopPreviewToolExecutor(...)` using `backend.execution` only.
- [x] Enforce frozen-definition and descriptor/grant integrity before provider dispatch.
- [x] Construct the exact selected-Shop `AuthorizedToolCall` from R7.
- [x] Apply the production-equivalent 10-second / 12-provider-request Tool budget.
- [x] Route Shopify Admin execution through the current selected-Shop offline session.
- [x] Route Policy Operations through the production registry without fabricated durable business state.
- [x] Correct runtime Platform/per-Shop External credential resolution per R11.
- [x] Route External HTTP execution through the production connection/credential machinery.
- [x] Update PreviewService conversation Tool execution to use only the selected-Shop executor.
- [x] Preserve independent fixture-backed Tool Authoring / Code Response Tool tests.
- [x] Add the full selected-Shop Tool execution regression matrix.
- [x] Keep human message execution disabled until C007.
- [x] Validate secret/telemetry/persistence safety.

## Interfaces / Contracts

### Consumes

From ARCH-024-COMMERCE-004/005:

```text
PreviewSelection = FEATURES
Feature-composed PreviewBundle / grant
PreviewConversationSnapshot
  snapshot.shop exact server-resolved Shop id/domain
  exact Tool definitions / Feature Behaviour
  frozen model + Platform/optional Shop instructions
selected Shop id carried into grant
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

- [x] Human Feature Test Conversations no longer execute Shopify/Policy/External Tools through fixture execution.
- [x] The selected Shop ID/domain come only from C005 `conversation.snapshot.shop` and are never accepted from browser domain input.
- [x] `bundle.grant.shopId` must equal `conversation.snapshot.shop.id`.
- [x] Conversation Tool execution uses `backend.execution` / the existing production `DefinitionExecutor`.
- [x] Exact frozen Tool revision definitions are used; later Tool publication does not alter a started conversation.
- [x] Descriptor/grant/snapshot mismatch fails closed before any provider request.
- [x] Shopify Admin Tools resolve the current selected-Shop offline session/token at Tool execution time.
- [x] Missing Shopify offline session produces bounded failure and never falls back to fixture facts.
- [x] Policy Operations receive the selected Shop identity and no fake durable recovery/customer/order state is created.
- [x] Platform External connections work with their global credential while the Tool call retains selected-Shop identity.
- [x] Per-Shop External connections can use only the exact selected Shop credential.
- [x] Credential rotation is observed by the next Tool invocation without recreating the Test Conversation.
- [x] Selected-Shop Tool execution uses a 10-second deadline and at most 12 provider reservations.
- [x] Caller cancellation propagates to provider execution.
- [x] `/api/studio/preview/tool-tests` and its retained fixture executor remain functional and separate.
- [x] The human Test Conversation message composer remains disabled after C006.
- [x] No Shopify/External secret is persisted into Preview conversation state, returned to the browser or added to telemetry.
- [x] No new durable business-state mutation is introduced by Test Conversation Tool execution.

## Validation

Before running Node commands, follow the workspace Node bootstrap policy.

Inspect `package.json` before running repository commands; do not invent missing scripts.

Required validation:

- [x] Focused tests including at minimum:

```text
tests/selected-shop-preview-tool-execution.test.ts
tests/preview-service.test.ts
tests/preview-integration.test.ts
tests/external-http-executor.test.ts or the accepted equivalent credential/external execution regression suite
```

- [x] Existing DefinitionExecutor tests covering Shopify Admin / Policy / External remain green.
- [x] Existing Tool Authoring / Code Response fixture Tool-test tests remain green.
- [x] Same-tick/cancellation/unknown Preview service tests affected by the port split remain green.
- [x] TypeScript typecheck using the repository-declared command.
- [x] Targeted ESLint for every changed TS/TSX file using the repository-declared lint capability.
- [x] Production build using the repository-declared build command.
- [x] Changed-file diagnostics contain no new errors.
- [x] `git diff --check`.
- [x] Static search proves the human conversation path no longer references `preview.myshopify.com`, `fixtureQuery(...)` or `backend.createFixtureExecution(...)`.
- [x] Static search proves retained `/api/studio/preview/tool-tests` still has its fixture-backed implementation.
- [x] Static/fixture inspection proves no secret-bearing field was added to `StoredConversation`, Preview result contracts, logs or browser props.

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
- C005 owns authored snapshot construction. C006 MUST treat `PreviewConversationSnapshot` as immutable input and must not reread current Shop domain, model, instructions, Feature Behaviour or Tool revision authoring state. Only operational credentials/sessions/connections remain live.
- The R11 Platform-connection correction is authorised because the existing production `ExternalHttpExecutionPort` always executes in a Shop turn, while Platform credentials are globally scoped. Do not broaden the correction into credential-administration redesign.
- C006 intentionally leaves the human message composer disabled. This allows real Tool-execution wiring to be reviewed independently before OpenRouter/model execution is enabled.

## Completion Report

### Status

Ready for Review

### Attempt 2 Rework — 2026-10-02

**Architect Review A1-R1: implemented.** In `src/commerce/integration/preview/adapters.ts`, the selected-Shop executor now fails closed when no manifest capability matches the exact `toolId + toolRevisionId`, accepts one or more matching capabilities, and compares every matching descriptor with the requested descriptor before dispatch. The single deduplicated grant-entry check and all frozen-definition checks remain unchanged. `tests/selected-shop-preview-tool-execution.test.ts` adds coverage for two distinct capabilities sharing one Tool revision with one grant entry containing both keys, plus a conflicting duplicate descriptor that returns `INCOMPATIBLE_VERSION` without calling `backend.execution`.

### Attempt 2 Validation Results

- Focused duplicate-capability matrix: `npm test -- tests/selected-shop-preview-tool-execution.test.ts` passed; 1 file, 8 tests.
- Complete focused C006 packet: Vitest passed 11 files and 102 tests, covering selected-Shop execution, Preview service/integration/routes/store/Redis, External HTTP/credentials, DefinitionExecutor, snapshot and Feature composition.
- Targeted ESLint over all 16 C006-changed TypeScript/TSX files: passed with no output.
- `npm run typecheck`: passed (`next typegen`, `tsc --noEmit`).
- `npm run build`: passed; emitted the existing Nunjucks dynamic-dependency warning.
- Changed-file diagnostics for both Attempt 2 files: no errors.
- Static audits: the human conversation service contains no `preview.myshopify.com`, fixture query/executor, or fixture response data references; independent `/api/studio/preview/tool-tests` routes and fixture executor remain. No credential-bearing field was added to Preview types/service.
- `git diff --check`: passed. No live Shopify or External network calls were made.

### Attempt 2 Execution Evidence

- Prepared claim: `in_progress`, attempt `2`, executor `copilot`, claimed `2026-10-02T00:34:11Z`; durable parent claim commit `976eba68e4aad52ca0fc8258aac8f1cb720de68b` was pushed.
- Dedicated worktrees reused without rerunning launcher, claim or synchronization: parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-024-COMMERCE-006`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-024-COMMERCE-006`. Both use `task/ARCH-024-COMMERCE-006`.
- Prepared evidence: parent start head `e3e960dd986ef786e69a94df18f645b8125acff4`; implementation start head `0fa6a8ad088886d4b9573b6abcd507c59003ff5e`; parent already included `origin/main`, implementation was current, and task-branch remote fast-forwards were not needed. Dependency ARCH-024-COMMERCE-005 was complete; recursive Database submodule was `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.
- Implementation commit `78257d26c0dbc08e261d10ee80221bef314667b2` is pushed; local and remote task heads match, and the implementation worktree is clean.
- Parent task/report changes are limited to this task file. The report branch was pushed and local/remote equality plus clean status were verified after publication.

No C007 work was started. The task is returned to review and is not marked complete.

### Files Changed

Implementation commit `0fa6a8ad088886d4b9573b6abcd507c59003ff5e` contains:

- `lib/discovery/admin-compiler.ts` — mechanically required correction: iterate `compiled.variables.entries()` so the required-variable check uses each mapped GraphQL variable name, not the `Map.values()` callback index. The selected-Shop DefinitionExecutor matrix exposed this defect while validating exact Admin query variables.
- `lib/preview/runtime.ts`
- `src/commerce/connections/credentials/index.ts`
- `src/commerce/integration/external/index.ts`
- `src/commerce/integration/preview/adapters.ts`
- `src/commerce/preview/service.ts`
- `src/commerce/preview/types.ts`
- `tests/external-credentials.test.ts`
- `tests/feature-preview-composition.test.ts`
- `tests/preview-integration.test.ts`
- `tests/preview-redis-lua.test.ts`
- `tests/preview-routes.test.ts`
- `tests/preview-service.test.ts`
- `tests/preview-store.test.ts`
- `tests/test-conversation-snapshot.test.ts`
- `tests/selected-shop-preview-tool-execution.test.ts`

### Work Completed

Feature-composed human Test Conversations now use a separate selected-Shop executor backed by `CommerceBackend.execution`. It validates the C005 snapshot, grant, descriptor and exact frozen definition before dispatch, constructs the bounded `AuthorizedToolCall`, and enforces the 10-second/12-reservation budget with cancellation propagation. Shopify sessions and External credentials resolve live at each invocation; Platform and per-Shop credential scopes are handled correctly. Preview conversation state no longer carries fixture-only execution data, while independent fixture-backed Tool tests remain supported. The composer remains disabled for C007. No durable business state or provider credentials are fabricated or persisted.

The selected-Shop regression matrix exercises the real `DefinitionExecutor` dependency seam for frozen definitions, selected-Shop identity, Shopify offline-session rotation/missing-session handling, Policy Operations without fabricated recovery state, Platform/per-Shop External credential selection and rotation, provider budget, cancellation, and deadline cleanup.

### Validation Results

Agent-executed validation passed:

- Focused Vitest command covering 11 files (`selected-shop-preview-tool-execution`, Preview service/integration/routes/client/store/Redis, External HTTP/credentials, DefinitionExecutor, snapshot and Feature composition): 11 files passed, 100 tests passed.
- Targeted ESLint over all 16 changed TypeScript/TSX files: passed with no output.
- `npm run typecheck`: passed (`next typegen`, `tsc --noEmit`).
- `npm run build`: passed; emitted only the existing Nunjucks dynamic-dependency warning.
- Changed production files and selected-Shop matrix diagnostics: no errors.
- `git diff --check`: passed for the staged implementation and parent task changes.
- Static inspection confirmed the human conversation path no longer references `preview.myshopify.com`, `fixtureQuery(...)` or `backend.createFixtureExecution(...)`; fixture references remain in the independent Tool-test executor.
- Static inspection confirmed the disabled composer message and Send control remain, and no access token, ciphertext, nonce, auth tag, auth header value, session body or credential-secret field was added to Preview/browser contracts.
- No live Shopify or External network calls were made. The full repository suite was not run; it is not required by this task.

Launcher/preparation evidence: dedicated parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-024-COMMERCE-006` and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-024-COMMERCE-006` were created fresh on `task/ARCH-024-COMMERCE-006`. Parent start head was `4e07e97cc70b9a0e796408a7389245e4ced95409`; implementation start head was `d60360a6fa7a16861c5b68a613379d43e81e7b37`. Both task remote fast-forwards were not needed; `origin/main` was already current. Dependency gate passed with ARCH-024-COMMERCE-005 complete. Recursive submodule sync/update passed; Database submodule was `cfeeb12456b4e05067a96857a8c47837d7e33bbd`. Attempt 1 was claimed by `copilot` at `2026-10-01T23:33:44Z`; durable parent claim commit `60e1e7629b2ecbc62336cb6b32ce705bcd8272f1` was pushed.

Implementation publication: local and remote `task/ARCH-024-COMMERCE-006` both point to `0fa6a8ad088886d4b9573b6abcd507c59003ff5e`; implementation worktree was clean after push. Parent review-report publication is recorded by the current parent task branch commit; local and remote equality and clean status were verified after push.

### Deviations

The focused matrix uncovered the narrow `lib/discovery/admin-compiler.ts` mapped-variable validation defect. The correction is included because it is mechanically required for production DefinitionExecutor Admin variable validation; no other scope was expanded.

### Assumptions

The prepared execution packet is authoritative for Attempt 1 isolation, dependency, submodule synchronization and claim evidence. Existing Nunjucks dynamic-dependency build warning is unchanged and unrelated to C006.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 — Changes Requested (2026-10-02).

The selected-Shop execution architecture is otherwise conformant: the human conversation path is separated from retained fixture Tool tests, `backend.execution` / the production `DefinitionExecutor` is reused, frozen definitions and selected-Shop identity are validated before provider dispatch, current Shopify sessions and External credentials remain live, the 10-second / 12-provider-request envelope is present, the composer remains locked for C007, and the submitted Completion Report contains the required dedicated-worktree / synchronization / recursive-submodule / claim / clean-remote evidence.

**A1-R1 — valid C004 compositions with more than one Capability using the same Tool revision are rejected.**

ARCH-024-COMMERCE-004 explicitly requires every Capability member to remain in the manifest while Tool definitions and `grantedTools` are deduplicated by exact Tool revision. Its accepted contract therefore permits multiple `manifest.capabilities` entries to carry the same `toolId + toolRevisionId`, with one deduplicated `grantedTools` entry whose `capabilityKeys` contains every Capability key using that revision.

The C006 selected-Shop executor currently does:

```ts
const manifestMatches = bundle.manifest.capabilities.filter(
  (item) =>
    item.toolDescriptor.toolId === tool.toolId
    && item.toolDescriptor.toolRevisionId === tool.toolRevisionId,
);

if (
  manifestMatches.length !== 1
  || canonicalJson(manifestMatches[0]!.toolDescriptor) !== canonicalJson(tool)
) {
  return incompatibleToolResult();
}
```

That `length !== 1` check makes a valid C004 composition fail with `INCOMPATIBLE_VERSION` before provider dispatch whenever two or more Capability members legitimately share one Tool revision. This contradicts the accepted C004 invariant and C006 R6, which requires that the descriptor **appears** in `bundle.manifest.capabilities`; it does not require the Tool revision to occur in exactly one Capability member.

Attempt 2 correction contract:

1. Keep the exact `toolId + toolRevisionId` manifest lookup, but accept one-or-more matching Capability members.
2. Fail closed when there are zero matching Capability members.
3. Because duplicate Capability members are valid, validate the requested descriptor against **every** matching Capability member (or an equivalent fail-closed check) so a conflicting duplicate descriptor still returns `INCOMPATIBLE_VERSION` before provider dispatch.
4. Preserve the single deduplicated `bundle.grant.grantedTools` integrity check and the frozen-definition checks.
5. Add focused selected-Shop regression coverage using a manifest with at least two distinct Capability members that share the same Tool revision and one deduplicated grant entry containing both Capability keys. Prove the valid Tool executes through `backend.execution`.
6. Add or retain a fail-closed regression proving a conflicting descriptor among matching duplicate Capability members does not dispatch the provider.
7. Rerun the complete C006 required validation and return the same task to review.
8. Do not begin COMMERCE-007.

No database, Shared, Admin, Background, Gateway, model-runtime, credential-administration, or broader Feature-composition redesign is requested.

### Reviewed Files

- `docs/decisions/commerce/ARCH-024/COMMERCE-006-execute-test-conversation-tools-against-selected-shop.md`
- `docs/decisions/commerce/ARCH-024/COMMERCE-004-compose-test-conversations-from-selected-features.md`
- `docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`
- `moda-interact-commerce/src/commerce/integration/preview/adapters.ts`
- `moda-interact-commerce/src/commerce/preview/service.ts`
- `moda-interact-commerce/src/commerce/preview/types.ts`
- `moda-interact-commerce/lib/preview/runtime.ts`
- `moda-interact-commerce/src/commerce/connections/credentials/index.ts`
- `moda-interact-commerce/src/commerce/integration/external/index.ts`
- `moda-interact-commerce/lib/discovery/admin-compiler.ts`
- `moda-interact-commerce/tests/selected-shop-preview-tool-execution.test.ts`
- `moda-interact-commerce/tests/feature-preview-composition.test.ts`
- `moda-interact-commerce/tests/preview-integration.test.ts`
- `moda-interact-commerce/tests/preview-service.test.ts`
- `moda-interact-commerce/tests/external-credentials.test.ts`
- `moda-interact-commerce/tests/test-conversation-snapshot.test.ts`

### Validation Reviewed

- Inspected the exact C006 implementation delta against the accepted C005 snapshot.
- Confirmed C004's accepted contract and regression fixture retain multiple Capability members sharing one Tool revision while deduplicating Tool/grant entries.
- Confirmed the current C006 `manifestMatches.length !== 1` guard rejects that valid manifest shape before `backend.execution.execute(...)`.
- Reviewed the submitted focused-validation evidence: 11 test files / 100 tests, targeted ESLint, TypeScript, production build, changed-file diagnostics, static audits and `git diff --check`.
- Confirmed the uploaded archive contains no installed dependency tree or Git metadata, so dependency-backed test/build commands and remote refs were not independently replayed in the review environment.

### Architecture Conformance

Changes Required.

The implementation conforms to the selected-Shop execution, frozen-definition, live-credential/session, fixture-separation, provider-budget, secret-safety, persistence and C007-lockout boundaries except for A1-R1. A1-R1 breaks the already-accepted C004 many-Capabilities-to-one-Tool composition invariant and must be corrected before C006 can become Complete.

### Follow-up

Return `ARCH-024-COMMERCE-006` to `ready` with Attempt 1 preserved and the execution claim cleared. The next authorized `/moda-task ARCH-024-COMMERCE-006` claim becomes Attempt 2.

`ARCH-024-COMMERCE-007` remains Pending until C006 is architect-accepted Complete.
