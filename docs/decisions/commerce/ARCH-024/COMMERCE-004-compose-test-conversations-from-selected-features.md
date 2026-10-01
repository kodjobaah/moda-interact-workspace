---
id: ARCH-024-COMMERCE-004
architecture_id: ARCH-024
title: Compose Test Conversations from selected Features
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
attempt: 1
depends_on:
  - ARCH-024-COMMERCE-001
enables:
  - ARCH-024-COMMERCE-005
created: 2026-09-30
updated: 2026-10-01
---

# Compose Test Conversations from selected Features

## Architecture

Architecture ID:

`ARCH-024`

Architecture document:

`docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`

Coordinator:

`moda_architect`

## Objective

Replace Release/Draft conversation composition at the Preview service boundary with one server-authoritative Feature composition contract:

```text
selected Feature IDs
        |
        v
server resolves every direct CommerceCapability under every selected Feature
        |
        v
server resolves each Capability's current published CommerceToolRevision
        |
        v
server resolves Feature Behaviour once per selected Feature
        |
        v
server builds one deterministic CommerceManifest + immutable Tool-definition snapshot
        |
        v
conversation stores that exact composition for all later turns
```

Selecting a Feature means **all direct Capabilities belonging to that Feature**. The browser MUST NOT submit Capability IDs, Tool IDs, Tool revision IDs, Feature Behaviour text, Tool definitions, Release IDs or response contracts for the Feature-composed conversation path.

This task is server-side composition only. It MUST NOT build the new Test Conversations UI, execute Tools against the selected real shop, or invoke OpenRouter.

## Context

ARCH-024-COMMERCE-001 removes the obsolete human-facing synthetic Preview composer but intentionally retains the conversation service/store/runtime seams for later ARCH-024 work.

The current backend still models conversation composition as:

```ts
PreviewSelection =
  | { kind: 'RELEASE'; releaseId: string }
  | {
      kind: 'DRAFT';
      capabilityIds: string[];
      toolRevisionIds: string[];
      responseContract?: unknown;
    };
```

and `createPreviewBundleLoader()` resolves that selection through `backend.saved.readSelection(...)`.

That is no longer the ARCH-024 product contract.

The replacement contract is Feature-driven. The current database already provides the required direct relationships:

```text
Feature
    1
    |
    *
CommerceCapability
    |
    +-- featureId -> Feature.id
    +-- toolId    -> CommerceTool.id
                     |
                     *
                 CommerceToolRevision
```

Feature Behaviour is stored in:

```text
CommerceFeatureConfiguration
    featureId       PK/FK -> Feature.id
    behaviourPrompt
```

A Feature may exist without a `CommerceFeatureConfiguration` row. The established Studio read model treats that case as an empty Behaviour prompt; this task MUST preserve that semantic.

The Shared `CommerceManifestSchema` currently permits at most 32 Capabilities and requires every `featureBehaviours` entry to correspond to a Feature represented by at least one Capability. This task MUST respect that published contract and MUST NOT modify `moda-interact-shared`.

ARCH-024 is pre-production. Existing development Preview conversation/Redis records do not require backwards compatibility with the old `RELEASE`/`DRAFT` conversation-selection shape.

## Scope

Primary implementation targets:

```text
moda-interact-commerce/src/commerce/preview/types.ts
moda-interact-commerce/src/commerce/integration/backend.ts
moda-interact-commerce/src/commerce/integration/preview/adapters.ts
moda-interact-commerce/src/commerce/preview/service.ts

moda-interact-commerce/tests/preview-service.test.ts
moda-interact-commerce/tests/preview-integration.test.ts
moda-interact-commerce/tests/preview-routes.test.ts
moda-interact-commerce/tests/backend-integration.test.ts
```

A focused new test file is allowed at exactly:

```text
moda-interact-commerce/tests/feature-preview-composition.test.ts
```

if separating the composition matrix keeps the existing Preview tests bounded.

Additional Commerce files may be changed only when mechanically required to carry the new Feature selection through the retained Preview conversation boundary. Every additional file MUST be named and justified in the Completion Report.

Do not modify:

```text
moda-interact-commerce/database/**
moda-interact-shared/**
moda-interact-admin/**
moda-interact-background/**
moda-interact-gateway/**
```

## Out of Scope

- Feature-selection UI; ARCH-024-COMMERCE-005 owns it.
- Loading/displaying effective active Model in the Test Conversations UI.
- Changing Commerce Studio Model selection.
- OpenRouter/LangChain model invocation; ARCH-024-COMMERCE-007 owns it.
- OpenRouter credential lookup/decryption.
- Executing Shopify/External/Policy Tools against the selected real shop; ARCH-024-COMMERCE-006 owns it.
- Replacing the retained synthetic Tool executor in this task.
- Removing `COMMERCE_PREVIEW_PROVIDER`, `COMMERCE_PREVIEW_MODEL` or `COMMERCE_PREVIEW_API_KEY`.
- Billing-plan, Subscription, Shop Feature preference or active-Release eligibility filtering.
- Per-Capability selection or exclusion.
- Creating/publishing Tool revisions.
- Creating/activating Releases.
- Database migrations.
- Shared-package changes.
- Changing ARCH-023 Platform/Shop Instruction semantics.
- LangGraph adoption.

## Requirements

### R1 — replace the conversation Preview selection with one exact Feature shape

In `src/commerce/preview/types.ts`, replace the conversation-facing `PreviewSelectionSchema` with the strict shape:

```ts
export const PreviewSelectionSchema = z.strictObject({
  kind: z.literal('FEATURES'),
  featureIds: z.array(SavedIdSchema)
    .min(1)
    .max(32)
    .refine((ids) => new Set(ids).size === ids.length, 'duplicate Feature id'),
});

export type PreviewSelection = z.infer<typeof PreviewSelectionSchema>;
```

The conversation Preview boundary MUST NOT accept:

```text
RELEASE
DRAFT
releaseId
capabilityIds
toolRevisionIds
responseContract
```

Do **not** remove the separate internal `CommerceSavedSelectionInput` `RELEASE`/`DRAFT` shapes from `src/commerce/integration/backend.ts` merely because the conversation boundary no longer uses them. Retained Tool-test/Code Response internals may still require those saved-selection operations until later cleanup proves otherwise.

Existing development Redis conversations encoded with the old `PreviewSelectionSchema` may be discarded/flushed. Do not add compatibility parsing for them.

### R2 — introduce one explicit Feature-composition backend port

In `src/commerce/integration/backend.ts`, add exactly these exported domain shapes, using the existing Shared `CommerceResponseContract` and local `CommerceToolDefinition` types rather than duplicating them:

```ts
export type CommerceFeatureCompositionResult = {
  kind: 'FEATURES';
  featureIds: string[];
  featureBehaviours: Array<{
    featureId: string;
    behaviourPrompt: string;
  }>;
  responseContract: CommerceResponseContract;
  responseContractHash: string;
  capabilities: Array<{
    capabilityId: string;
    key: string;
    featureId: string;
    toolId: string;
    toolRevisionId: string;
    position: number;
  }>;
  tools: Array<{
    toolId: string;
    revisionId: string;
    definition: CommerceToolDefinition;
    contentHash: string;
  }>;
};

export type CommerceFeatureComposition = {
  resolve(input: {
    principal: Principal;
    featureIds: string[];
  }): Promise<CommerceFeatureCompositionResult>;
};
```

Add to `CommerceBackend`:

```ts
featureComposition: CommerceFeatureComposition;
```

Add to `CommerceBackendDependencies`:

```ts
featureComposition?: CommerceFeatureComposition;
```

`createCommerceBackend(...)` MUST wire:

```ts
featureComposition:
  dependencies.featureComposition ?? createPrismaFeatureComposition(dependencies.prisma)
```

Do not overload `CommerceSavedSelection` with Feature composition. `saved` remains the retained saved Release/Draft read boundary for internal consumers; `featureComposition` is the new Feature-composed conversation boundary.

### R3 — authorize before Feature composition reads

`createPrismaFeatureComposition(prisma)` MUST call the existing `authorizeStaff(prisma, principal)` before any Feature/Capability/Tool read.

Do not introduce a weaker authorization path.

Development bypass continues to use the existing `authorizeStaff` behaviour.

### R4 — preserve selected Feature order exactly

`featureIds` input order is semantically significant and MUST be preserved exactly.

The resolver MAY issue one bounded `Feature` query using `id IN (...)`, but MUST NOT depend on PostgreSQL/Prisma `IN` result order.

After loading, construct:

```ts
const featureById = new Map(rows.map((row) => [row.id, row]));
const selectedFeatures = input.featureIds.map((id) => featureById.get(id));
```

Required failure:

```text
any requested Feature missing -> LifecycleError('NOT_FOUND', ...)
```

Do not silently omit an unknown Feature.

### R5 — load the exact Feature graph in one bounded composition read

The Feature query MUST obtain enough data to resolve the composition without N+1 per-Capability or per-Tool reads.

The required logical include/select is:

```text
Feature
  id
  key
  commerceFeatureConfiguration
    behaviourPrompt
  commerceCapabilities
    id
    key
    featureId
    toolId
    tool
      id
      revisions
        where status = PUBLISHED
        orderBy revisionNumber DESC, id ASC
        take 1
        id
        toolId
        definition
        contentHash
```

The exact Prisma syntax may follow generated-client constraints, but the resulting query plan MUST remain bounded and MUST NOT perform one database query per Capability.

### R6 — selecting a Feature includes every direct Capability

For each selected Feature, include every direct current `CommerceCapability` whose `featureId` equals that Feature ID.

Do **not** filter composition using:

```text
Feature.active
Feature.activationMode
Feature.systemRequired
CommerceCapability.enabled
CommerceTool.enabled
ShopFeaturePreference
Subscription
MerchantPricingPlanFeature
BillingPlanFeature
CommerceRelease
CommerceReleasePointer
production entitlement
```

These are not authoring composition selectors.

A selected Feature with zero direct Capabilities MUST fail the whole composition with:

```text
LifecycleError('UNAVAILABLE', 'Selected Feature has no Capabilities')
```

Do not silently accept a selected Feature that cannot be represented by the current published `CommerceManifest` contract.

### R7 — Capability ordering is deterministic and independent of database row order

Within each selected Feature, sort its direct Capabilities by exactly:

```text
key ASC using String.localeCompare
then id ASC using String.localeCompare
```

Flatten in selected Feature order:

```text
featureIds[0] sorted Capabilities
featureIds[1] sorted Capabilities
...
```

Assign global positions exactly:

```text
0, 1, 2, ... N-1
```

If total resolved Capabilities exceed the Shared `CommerceManifestSchema` maximum of 32, fail the whole composition with `LifecycleError('UNAVAILABLE', ...)` before returning a partial result.

Do not truncate.

### R8 — each Capability resolves exactly one current published Tool revision

For each Capability's Tool, resolve exactly:

```text
status = PUBLISHED
orderBy:
  revisionNumber DESC
  id ASC
take = 1
```

Required failures:

```text
Capability has no Tool relation               -> UNAVAILABLE
Tool has no PUBLISHED revision                -> UNAVAILABLE
PUBLISHED definition fails Commerce schema    -> UNAVAILABLE
```

Use `CommerceToolDefinitionSchema.safeParse(...)`.

Do not fall back to a DRAFT revision.
Do not use Release membership to choose a revision.
Do not skip only the invalid Capability.

If multiple Capabilities reference the same Tool and therefore the same current published revision:

```text
keep every Capability member
but deduplicate `tools` by exact revisionId
```

If the same Tool identity somehow resolves to conflicting revision/definition data within one composition, fail closed as `UNAVAILABLE`.

### R9 — Feature Behaviour is resolved once per selected Feature

For each selected Feature, set:

```ts
behaviourPrompt = feature.commerceFeatureConfiguration?.behaviourPrompt ?? '';
```

Return exactly one `featureBehaviours` entry per selected Feature, in exact `featureIds` input order.

Do not derive Feature Behaviour from Capabilities.
Do not duplicate Feature Behaviour once per Capability.
Do not read Behaviour from an active Release snapshot.

Because R6 rejects zero-Capability Features, every `featureBehaviours.featureId` is represented by at least one returned Capability and remains valid under the current Shared `CommerceManifestSchema` invariant.

### R10 — Feature composition always uses the canonical empty response contract

For `FEATURES`, use exactly:

```ts
EMPTY_RESPONSE_CONTRACT
```

and calculate its canonical hash with the existing Commerce response-contract hash helper.

The Feature composition path MUST NOT accept or derive a response contract from:

```text
browser input
active Release
selected Release
Release pointer
```

### R11 — build one deterministic synthetic manifest identity

`createPreviewBundleLoader()` MUST stop calling `backend.saved.readSelection(...)` for the conversation Feature path and call:

```ts
backend.featureComposition.resolve({
  principal,
  featureIds: selection.featureIds,
})
```

For the required `CommerceManifest.releaseId`, create a synthetic non-durable ID exactly as:

```text
preview-features-<sha256 hex>
```

The SHA-256 input MUST be the JSON serialization of this already-deterministically-ordered object:

```ts
{
  featureIds,
  featureBehaviours,
  capabilities: capabilities.map((capability) => ({
    capabilityId: capability.capabilityId,
    key: capability.key,
    featureId: capability.featureId,
    toolId: capability.toolId,
    toolRevisionId: capability.toolRevisionId,
    position: capability.position,
  })),
  tools: tools.map((tool) => ({
    toolId: tool.toolId,
    revisionId: tool.revisionId,
    contentHash: tool.contentHash,
  })),
}
```

Before hashing, sort `tools` by:

```text
revisionId ASC
```

Do not use a real `CommerceRelease.id` and do not create a Release row.

### R12 — manifest construction is exact

For the Feature composition, build `CommerceManifestSchema` with:

```text
contractVersion        = commerce.v1
releaseId              = synthetic R11 identity
runnerCompatibility    = ^1.0.0
capabilities           = R7 ordered Capability members with descriptors from exact R8 revisions
featureBehaviours      = R9 ordered Feature Behaviours
selectedCapabilityKeys = Capability keys in exact manifest Capability order
grantedTools           = deduplicated exact Tool revisions + all Capability keys using each revision
responseContract       = EMPTY_RESPONSE_CONTRACT
responseContractHash   = canonical empty response-contract hash
```

`grantedTools` MUST be deterministic. Order the deduplicated Tools by the position of the first Capability that references each Tool revision.

For each granted Tool, `capabilityKeys` MUST follow manifest Capability order.

Parse the complete object with `CommerceManifestSchema`; any failure becomes `PreviewError('UNAVAILABLE')` at the Preview adapter boundary.

### R13 — freeze exact Tool definitions and Feature Behaviour into the existing conversation state

The Feature-composed `PreviewLoadedBundle.snapshot` MUST contain:

```text
definitions
    one entry per unique exact Tool revision
    revisionId
    parsed definition

prompts
    one entry for each NON-EMPTY Feature Behaviour
    in selected Feature order
```

Prompt names MUST use exactly:

```text
commerce/test-conversation/feature/<featureId>
```

Empty Feature Behaviour remains present in `manifest.featureBehaviours` but MUST NOT be emitted into `PreviewPromptSchema`, because that schema requires non-empty text.

The stored conversation already persists:

```text
selection.featureIds
bundle.manifest
snapshot.definitions
snapshot.prompts
```

That set is the **Feature-composition portion** of the later Conversation Configuration Snapshot. Do not duplicate Capability/Tool arrays into another new persisted object in this task.

After conversation creation, later edits to:

```text
Feature Behaviour
Capability membership
Tool publication
Tool definition
```

MUST NOT alter the stored conversation composition.

A new conversation is required to pick up those authoring changes.

### R14 — do not change Model, selected-shop Tool execution or Instruction semantics here

This task MUST NOT add active Model fields to the snapshot and MUST NOT resolve OpenRouter credentials.

It also MUST NOT replace the retained synthetic execution context yet.

Later tasks own:

```text
ARCH-024-COMMERCE-005
    human Feature selector + selected-shop start contract

ARCH-024-COMMERCE-006
    real selected-shop Tool execution

ARCH-024-COMMERCE-007
    effective active model + OpenRouter execution
```

ARCH-023 remains frozen; do not change Platform/Shop Instruction storage or resolution in this task.

### R15 — read-only authoring composition

Resolving a Feature composition MUST NOT write any authoring/business state:

```text
Feature
CommerceFeatureConfiguration
CommerceCapability
CommerceTool
CommerceToolRevision
CommerceRelease
CommerceReleasePointer
ShopFeaturePreference
Subscription/Billing
```

Normal Preview conversation/Redis state written by `PreviewService.startConversation()` is allowed and remains outside the resolver transaction boundary.

### R16 — Preview errors are bounded and do not expose definitions or database detail

Map expected composition failures to existing bounded Preview/Lifecycle error codes:

```text
unknown Feature                         -> NOT_FOUND
zero-Capability Feature                 -> UNAVAILABLE
>32 total Capabilities                  -> UNAVAILABLE
missing published Tool revision         -> UNAVAILABLE
invalid Tool definition                 -> UNAVAILABLE
manifest/snapshot validation failure    -> UNAVAILABLE
staff authorization failure             -> DENIED/FORBIDDEN through existing mapping
```

Do not include Tool definitions, Behaviour text, database error bodies, SQL, credentials or stack traces in client-visible messages.

## Work Items

- [x] Replace conversation `PreviewSelectionSchema` with strict `FEATURES + featureIds` selection.
- [x] Add `CommerceFeatureCompositionResult` and `CommerceFeatureComposition` to the Commerce backend boundary.
- [x] Implement `createPrismaFeatureComposition()` using existing staff authorization.
- [x] Resolve selected Features in input order without relying on `IN` query order.
- [x] Resolve all direct Capabilities with deterministic Feature/Capability ordering.
- [x] Fail closed for zero-Capability Features and compositions exceeding 32 Capabilities.
- [x] Resolve exact current published Tool revisions and parse definitions.
- [x] Resolve Feature Behaviour once per selected Feature, defaulting missing configuration to empty text.
- [x] Use `EMPTY_RESPONSE_CONTRACT` and its canonical hash.
- [x] Build deterministic synthetic `preview-features-<sha256>` manifest identity.
- [x] Build and validate deterministic manifest/granted-Tool ordering.
- [x] Freeze exact Tool definitions and non-empty Feature Behaviour prompts in the existing snapshot.
- [x] Preserve internal Release/Draft saved-selection support still required outside conversation composition.
- [x] Add focused unit/integration regressions for every acceptance case below.

## Interfaces / Contracts

Produces the conversation composition input:

```ts
type PreviewSelection = {
  kind: 'FEATURES';
  featureIds: string[]; // 1..32, unique, order significant
};
```

Produces the backend result:

```ts
type CommerceFeatureCompositionResult = {
  kind: 'FEATURES';
  featureIds: string[];
  featureBehaviours: Array<{
    featureId: string;
    behaviourPrompt: string;
  }>;
  responseContract: CommerceResponseContract;
  responseContractHash: string;
  capabilities: Array<{
    capabilityId: string;
    key: string;
    featureId: string;
    toolId: string;
    toolRevisionId: string;
    position: number;
  }>;
  tools: Array<{
    toolId: string;
    revisionId: string;
    definition: CommerceToolDefinition;
    contentHash: string;
  }>;
};
```

Consumes existing database relationships only. No new database or Shared contract is introduced by this task.

## Dependencies

- `ARCH-024-COMMERCE-001`

This dependency is the UI/runtime ownership handoff: COMMERCE-001 removes the obsolete human Preview composition while deliberately retaining the backend conversation/runtime seams that this task composes from selected Features. COMMERCE-003 model-selection UI is not an implementation dependency.

## Enables

- `ARCH-024-COMMERCE-005`

## Acceptance Criteria

- [x] Conversation Preview accepts exactly `{ kind: 'FEATURES', featureIds }`; `RELEASE`/`DRAFT` are not accepted by `PreviewSelectionSchema`.
- [x] `featureIds` must contain 1..32 unique saved IDs and input order is preserved exactly.
- [x] Unknown Feature ID fails the whole composition as `NOT_FOUND`.
- [x] A selected Feature with zero direct Capabilities fails the whole composition as `UNAVAILABLE`.
- [x] Feature.active, Capability.enabled, Tool.enabled, billing, Shop preferences and Release membership do not filter the selected Feature composition.
- [x] Capabilities are ordered selected-Feature order, then `key ASC`, then `id ASC`, with global positions `0..N-1`.
- [x] More than 32 resolved Capabilities fails; nothing is truncated.
- [x] Every Capability uses the current `PUBLISHED` Tool revision ordered `revisionNumber DESC, id ASC`.
- [x] Missing/invalid published Tool revision fails the whole composition; no Capability is silently dropped and no DRAFT is substituted.
- [x] Feature Behaviour is resolved once per selected Feature in selected order and missing configuration means `''`.
- [x] The Feature path always uses `EMPTY_RESPONSE_CONTRACT` and canonical hash.
- [x] Synthetic manifest identity is deterministic and changes when Feature order, Behaviour, Capability membership, Tool revision or Tool content hash changes.
- [x] Multiple Capabilities may share one Tool revision; Capability members remain distinct while Tool definition/grant entries are deduplicated deterministically.
- [x] Stored conversation selection + manifest + snapshot preserve the exact Feature composition after later authoring changes.
- [x] Feature composition performs no durable authoring/business writes.
- [x] Internal saved `RELEASE`/`DRAFT` selection remains available only to retained non-conversation consumers.
- [x] No Model/OpenRouter/credential or real selected-shop Tool-execution behaviour is introduced by this task.

## Validation

Before the first Node-related command:

```bash
command -v node >/dev/null 2>&1 || \
  source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"
```

Inspect `package.json` before running validation and use the repository's declared commands.

Required focused tests:

```bash
npx vitest run \
  tests/feature-preview-composition.test.ts \
  tests/preview-service.test.ts \
  tests/preview-integration.test.ts \
  tests/preview-routes.test.ts \
  tests/backend-integration.test.ts
```

If `tests/feature-preview-composition.test.ts` was not created because the cases were placed into existing focused suites, omit only that filename and record exactly where every required composition case lives.

Required static validation:

```bash
npm run typecheck
npm run build

git diff --check
```

Run targeted ESLint over every changed `.ts`/`.tsx` source/test file, for example:

```bash
npx eslint \
  src/commerce/preview/types.ts \
  src/commerce/integration/backend.ts \
  src/commerce/integration/preview/adapters.ts \
  src/commerce/preview/service.ts \
  tests/feature-preview-composition.test.ts \
  tests/preview-service.test.ts \
  tests/preview-integration.test.ts \
  tests/preview-routes.test.ts \
  tests/backend-integration.test.ts
```

Adjust the ESLint file list to the actual changed files; do not lint nonexistent optional files.

If a required validation cannot execute, leave it unchecked and record the exact blocker in the Completion Report. Do not invent replacement validation outside this task.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

1. finish the Completion Report;
2. set this task to `review`;
3. clear no architecture-owned coordination state;
4. return control to `moda_architect`;
5. **STOP**.

Do not start ARCH-024-COMMERCE-005 or any adjacent Preview/UI/runtime work.

## Implementation Notes

- This task intentionally introduces a dedicated `featureComposition` backend boundary instead of extending the retained `saved` Release/Draft boundary. That keeps the new product concept independent of old saved-selection mechanics.
- Do not introduce another Feature/Capability contract in Shared merely for this repository-local composition read. The cross-service runtime contract remains the existing published Commerce manifest/runner contract.
- The current Shared manifest cannot represent a Behaviour-only selected Feature with zero Capabilities. This task therefore fails such a selection rather than silently losing it or changing Shared as a side effect.
- `PreviewFrozenSnapshot` is reused for the exact Tool-definition/non-empty Feature-Behaviour **composition fragment** only. ARCH-024-COMMERCE-005 is the single owner that atomically extends that fragment at Start Conversation into the complete human Conversation Configuration Snapshot (Shop + model + instructions + composition). ARCH-024-COMMERCE-006 and ARCH-024-COMMERCE-007 consume that frozen snapshot and MUST NOT add authored snapshot fields later.

## Completion Report

### Status

Ready for Review

### Files Changed

- `src/commerce/preview/types.ts`: strict Feature-only conversation selection contract.
- `src/commerce/integration/backend.ts`: explicit composition port, Prisma resolver, authorization, deterministic ordering, validation, and backend default wiring.
- `src/commerce/integration/preview/adapters.ts`: Feature resolver use, synthetic manifest identity, deterministic manifest/grants, snapshot definitions/prompts, and bounded lifecycle error mapping. Internal saved Release/Draft access remains for Tool-test consumers.
- `tests/feature-preview-composition.test.ts`: strict selection and resolver/adapter composition matrix, including no-filtering, ordering, failures, deduplication, identity changes, freezing, and bounded errors.
- `tests/backend-integration.test.ts`: backend Feature-composition wiring coverage.
- `tests/preview-integration.test.ts`: Feature selection/composition and immutable snapshot integration coverage; retained saved-selection Tool-test coverage.
- `tests/preview-routes.test.ts` and `tests/preview-service.test.ts`: use the strict Feature selection shape at the conversation boundary.
- `tests/preview-store.test.ts` and `tests/preview-redis-lua.test.ts`: mechanically update persisted conversation fixtures to the new Feature selection shape; no store/Redis production behavior changed.

### Work Completed

- Replaced the conversation-facing `RELEASE`/`DRAFT` selector with a strict, unique 1..32 `FEATURES + featureIds` contract. Existing internal `CommerceSavedSelectionInput` Release/Draft operations remain available to non-conversation Tool-test consumers.
- Added `CommerceFeatureCompositionResult` / `CommerceFeatureComposition` and wired `createCommerceBackend()` to default to `createPrismaFeatureComposition()` while preserving dependency injection.
- Implemented a single bounded Feature graph read after `authorizeStaff()`. Requested Feature order is reconstructed explicitly; all direct Capabilities are included without activation, enabled-state, billing, preference, or Release filters. Capabilities sort by key/id and receive global positions. Missing Features, empty Features, over-32 composition, missing Tools/revisions, invalid definitions, and conflicting Tool/revision data fail closed.
- Resolved current published revisions with `revisionNumber DESC, id ASC`, retained each Capability member, deduplicated Tools by exact revision, returned one Behaviour per Feature with the empty-configuration default, and used the canonical empty response contract/hash.
- Rebuilt the Preview manifest with the deterministic `preview-features-<sha256>` identity, exact ordered descriptors and grants, validated it with `CommerceManifestSchema`, and froze unique definitions plus non-empty Feature Behaviour prompts named `commerce/test-conversation/feature/<featureId>` in the existing conversation snapshot.
- Kept model/provider configuration, selected-shop execution, Instruction resolution, and retained synthetic Tool execution semantics outside this change.
- Launcher preparation packet: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-024-COMMERCE-004`, branch `task/ARCH-024-COMMERCE-004`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-024-COMMERCE-004`, branch `task/ARCH-024-COMMERCE-004`. Dedicated worktrees were created for this task; the shared workspace/source checkouts were not switched or mutated for implementation, and no other task worktree was reused.
- Launcher synchronization: parent remote task branch fast-forward `not-needed`, parent `origin/main` incorporation `already-current`; implementation remote task branch fast-forward `not-needed`, implementation `origin/main` incorporation `already-current`.
- Launcher recursive submodule setup: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; `database` initialized at recorded commit `15859f16a7b9a889df8f70e1ecc29b27df8e31de`.
- Claim: Attempt 1, executor `copilot`, claimed at `2026-10-01T16:11:34Z`; parent claim commit `6749a8acf2cd727dde69c36aee16776d73cd02b0` was committed and pushed by the launcher.
- Implementation commit `9834f4694f216dac082d7620f349712d2f1d4763` (`task(ARCH-024-COMMERCE-004): compose previews from features`) is pushed to `origin/task/ARCH-024-COMMERCE-004`. Final implementation worktree was clean at that commit; the parent worktree was clean at its claim commit before this report update. No database gitlink was changed.

### Validation Results

- PASS: `npx vitest run tests/feature-preview-composition.test.ts tests/preview-service.test.ts tests/preview-integration.test.ts tests/preview-routes.test.ts tests/backend-integration.test.ts` — 5 files, 52 tests passed.
- PASS: `npx vitest run tests/feature-preview-composition.test.ts tests/preview-service.test.ts tests/preview-integration.test.ts tests/preview-routes.test.ts tests/backend-integration.test.ts tests/preview-store.test.ts tests/preview-redis-lua.test.ts` — 7 files, 65 tests passed. The two additional suites cover the mechanically updated persisted-store/Redis selection fixtures.
- PASS: `npm run typecheck` — Next route types generated; `tsc --noEmit` passed.
- PASS: `npm run build` — production build passed. Existing Nunjucks dynamic-dependency warnings were emitted from `node-loaders.js`; build completed successfully.
- PASS: `npx eslint src/commerce/preview/types.ts src/commerce/integration/backend.ts src/commerce/integration/preview/adapters.ts tests/feature-preview-composition.test.ts tests/backend-integration.test.ts tests/preview-integration.test.ts tests/preview-routes.test.ts tests/preview-service.test.ts tests/preview-store.test.ts tests/preview-redis-lua.test.ts` — passed with no reported issues.
- PASS: `git diff --check` — passed.

### Deviations

No scope deviation. `tests/preview-store.test.ts` and `tests/preview-redis-lua.test.ts` were the only additional files beyond the named primary targets; they were required to migrate retained storage test fixtures to the new strict selection shape.

### Assumptions

Per the task contract, legacy development Redis conversations encoded with the old Release/Draft selection schema may be discarded; no compatibility parser was added.

### Unresolved Issues

None.

### Architectural Concerns

None. The implementation stays within `moda-interact-commerce`; no Shared contract, schema, migration, UI, Model/OpenRouter, selected-shop execution, or ARCH-023 Instruction change was introduced.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted at Attempt 1. The implementation conforms to the ARCH-024 Feature-composed Test Conversation boundary. The conversation-facing selector is strict `FEATURES + featureIds`; the separate saved Release/Draft boundary remains available only to retained non-conversation consumers.

`createPrismaFeatureComposition()` uses the existing staff authorization before the Feature read, reconstructs selected Feature order explicitly, performs one bounded Feature-graph read, includes every direct Capability without active/enabled/entitlement/Release filtering, orders Capabilities deterministically, fails closed for missing/empty/oversized composition, resolves the current published Tool revision, validates Tool definitions, deduplicates exact revisions, preserves one Behaviour per selected Feature, and uses the canonical empty response contract/hash.

The Preview adapter consumes only `featureComposition` for conversation composition, builds the required deterministic `preview-features-<sha256>` identity, validates the complete Commerce manifest, orders grants by first Capability use, and freezes the resolved Tool definitions plus non-empty Feature Behaviour prompts into the existing snapshot. The retained Tool-test executor continues to use the saved DRAFT lookup boundary. No Model/OpenRouter, real selected-Shop Tool execution, database, Shared-package, Admin, Background or Gateway behaviour was introduced.

The two additional changed test files (`preview-store.test.ts` and `preview-redis-lua.test.ts`) are mechanically required fixture migrations for the strict Feature selection shape and remain within task scope.

### Reviewed Files

- `moda-interact-commerce/src/commerce/preview/types.ts`
- `moda-interact-commerce/src/commerce/integration/backend.ts`
- `moda-interact-commerce/src/commerce/integration/preview/adapters.ts`
- `moda-interact-commerce/src/commerce/preview/service.ts`
- `moda-interact-commerce/tests/feature-preview-composition.test.ts`
- `moda-interact-commerce/tests/backend-integration.test.ts`
- `moda-interact-commerce/tests/preview-integration.test.ts`
- `moda-interact-commerce/tests/preview-routes.test.ts`
- `moda-interact-commerce/tests/preview-service.test.ts`
- `moda-interact-commerce/tests/preview-store.test.ts`
- `moda-interact-commerce/tests/preview-redis-lua.test.ts`
- `moda-interact-commerce/database/prisma/schema.prisma` (relationship verification only; unchanged by task)
- `docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`
- `docs/decisions/commerce/ARCH-024/COMMERCE-004-compose-test-conversations-from-selected-features.md`

### Validation Reviewed

Submitted evidence records:

- required focused Vitest command: 5 files / 52 tests passed;
- extended Preview/store/Redis set: 7 files / 65 tests passed;
- `npm run typecheck` passed;
- targeted ESLint over every changed TypeScript source/test file passed;
- `npm run build` passed with the pre-existing Nunjucks dynamic-dependency warnings only;
- `git diff --check` passed;
- implementation commit `9834f4694f216dac082d7620f349712d2f1d4763` and parent report commit `81bc7ce8` were reported pushed with both task worktrees clean and remote-aligned.

The submitted snapshot does not include installed `node_modules`, so the architect did not rerun the Node validation locally; the changed source and focused tests were inspected directly against the task contract and the recorded validation evidence.

### Architecture Conformance

Conforms. COMMERCE-004 establishes the server-authoritative Feature-composition fragment required by ARCH-024 without crossing into COMMERCE-005 UI/model/instruction snapshot completion, COMMERCE-006 selected-Shop execution, or COMMERCE-007 OpenRouter execution.

### Follow-up

No correction required. `ARCH-024-COMMERCE-005` remains Pending because `ARCH-024-COMMERCE-002` is not yet Complete; acceptance of COMMERCE-004 alone does not satisfy the full COMMERCE-005 dependency set.
