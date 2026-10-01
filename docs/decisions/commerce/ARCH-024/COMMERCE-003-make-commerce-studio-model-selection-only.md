---
id: ARCH-024-COMMERCE-003
architecture_id: ARCH-024
title: Make Commerce Studio model selection-only
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-024-COMMERCE-002
  - ARCH-024-ADMIN-002
enables: []
created: 2026-09-30
updated: 2026-10-01
---

# Make Commerce Studio model selection-only

## Architecture

Architecture ID:

`ARCH-024`

Architecture document:

`docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`

Coordinator:

`moda_architect`

## Objective

Remove Model Catalogue administration from Commerce Studio and leave Agent Configuration responsible only for selecting the one active Platform model and an optional explicit Shop model override from the models that Admin has made available. When the Shop override is cleared, Studio must display the inherited winner resolved by COMMERCE-002: current Price Plan model when configured, otherwise Platform.

The completed behaviour must be:

```text
Admin
    creates Model Availability
    creates/edits/enables/disables Catalogue Entries
    assigns each Catalogue Entry to one Availability

Commerce Studio
    PLATFORM configuration
        selects exactly one Platform-available model

    SHOP configuration
        selects one effectively available model
        OR
        stores modelId = NULL for inherited resolution:
            Price Plan model when configured
            otherwise Platform model
```

Commerce Studio MUST NOT create, edit, enable, disable, reassign or otherwise administer `CommerceModelAvailability`, `CommerceModelCatalogueEntry` or `CommerceOpenRouterCredential`.

## Context

The integrated ARCH-021 baseline currently renders Model Catalogue administration inside Commerce Studio:

```text
src/studio/agent-configuration/platform-model-configuration.tsx
    Platform model selector
    +
    Model catalogue create form
    +
    Model catalogue edit forms
    +
    Enable/disable actions
```

and the Shop configuration currently loads the global catalogue and filters it in the browser:

```text
listModelCatalogue()
    -> all catalogue entries
    -> catalogue.filter(item => item.enabled)
```

That boundary is no longer valid under ARCH-024.

ARCH-024-DATABASE-001 makes Catalogue Entries belong to Platform or Shop Model Availability. ARCH-024-ADMIN-001/002 make Admin the owner of Availability and Catalogue administration. ARCH-024-COMMERCE-002 provides the authoritative Commerce read/write boundary:

```ts
listPlatformAvailableModels()
listEffectiveAvailableModels(shopId)
assertModelSelectable(...)
```

and retains the durable Agent Configuration representation:

```text
Platform modelId
    one selected Platform model

Shop modelId = NULL
    no explicit Shop override
    -> effective resolver uses Price Plan model when configured
    -> otherwise Platform model

Shop modelId != NULL
    explicit Shop selection
```

This task performs the ownership/UI cutover only. It MUST NOT implement Test Conversations, OpenRouter execution or model credential management.

ARCH-023 is frozen. Prompt/Instruction authoring and resolution are not redesigned by this task.

## Scope

Primary implementation targets:

```text
moda-interact-commerce/src/studio/agent-configuration/platform-model-configuration.tsx
moda-interact-commerce/src/studio/agent-configuration/shop-agent-configuration.tsx
moda-interact-commerce/src/studio/agent-configuration/agent-configuration-screen.tsx
moda-interact-commerce/src/studio/agent-configuration/model-contracts.ts
moda-interact-commerce/src/studio/agent-configuration/model-server-actions.ts

moda-interact-commerce/src/commerce/agent-configuration/model-service.ts

moda-interact-commerce/tests/agent-configuration-model-ui.test.tsx
moda-interact-commerce/tests/agent-configuration-shop-ui.test.tsx
moda-interact-commerce/tests/agent-configuration-server-actions.test.ts
moda-interact-commerce/tests/agent-configuration-production.test.tsx

moda-interact-commerce/app/styles.css
```

Additional files may be changed only when required to remove now-dead Catalogue administration references or keep current focused tests/typecheck valid. Every additional file MUST be identified and justified in the Completion Report.

Do not modify the nested `database/` schema in this task.

Do not change the Shared package version established by ARCH-024-COMMERCE-002 unless the architect explicitly revises the dependency contract.

## Out of Scope

- Admin Model Availability implementation; ARCH-024-ADMIN-001 owns it.
- Admin Model Catalogue implementation; ARCH-024-ADMIN-002 owns it.
- Admin OpenRouter credential management.
- Editing `MerchantPricingPlan.commerceModelId`; ARCH-024-ADMIN-004 owns Price Plan model product configuration.
- Creating, editing, enabling, disabling or reassigning Catalogue Entries from Commerce Studio.
- Model Availability mutation from Commerce Studio.
- OpenRouter credential lookup/decryption.
- LangChain/OpenRouter model invocation.
- Test Conversation Feature composition.
- Test Conversation UI.
- Test Conversation Tool execution.
- Background production model execution.
- Gateway/environment cutover.
- Merchant-facing model selection; merchants do not select models.
- Changing the authoritative availability/selection rules implemented by ARCH-024-COMMERCE-002.
- Changing ARCH-023 Platform/Shop Instruction or prompt ownership/semantics.
- Adding a second "active" flag to Model Catalogue Entry or Model Availability.
- Automatically clearing an explicit invalid Shop model selection.

## Requirements

### R1 — Commerce Studio owns selection only

After this task, the Commerce Studio model boundary is exactly:

```text
READ
    list Platform-available models
    list effective Shop-available models
    read Platform Agent Configuration
    read Shop Agent Configuration

WRITE
    set Platform modelId
    set Shop modelId
    clear Shop modelId -> NULL (Use inherited model: Price Plan -> Platform)
```

The Studio MUST NOT expose or call Catalogue/Availability/Credential administration operations.

### R2 — Remove the global Catalogue read API from the Studio boundary

Remove the Studio-facing global Catalogue read:

```ts
listModelCatalogue()
```

The Platform selector MUST use only:

```ts
listPlatformAvailableModels()
```

The Shop selector MUST use only:

```ts
listEffectiveAvailableModels(shopId)
```

Do not fetch the complete catalogue and filter it in React.

Do not add another endpoint that returns all Catalogue Entries to Commerce Studio.

### R3 — Remove Catalogue mutation contracts and Server Actions from Commerce

Remove these Studio contracts if they still exist after ARCH-024-COMMERCE-002:

```ts
CreateModelCatalogueEntryInput
UpdateModelCatalogueEntryInput
SetModelEnabledInput
```

Remove these Studio Server Actions:

```ts
createModelCatalogueEntry(...)
updateModelCatalogueEntry(...)
setModelCatalogueEnabled(...)
```

Remove corresponding `ModelConfigurationService`/port methods that exist solely to support Commerce Catalogue administration:

```text
listCatalogue / listModelCatalogue
createCatalogueEntry
updateCatalogueEntry
setCatalogueEnabled
```

Do not retain dead compatibility aliases.

Do not remove the selection operations:

```text
setPlatformModel
setShopModel
clearShopModel
getPlatformAgentConfiguration
getShopAgentConfiguration
listPlatformAvailableModels
listEffectiveAvailableModels
```

If `getPlatformModelSelection` / `getShopModelSelection` have no remaining source consumer after this cutover, remove those Studio-facing wrappers/actions as dead compatibility surface and update their tests. Do not remove a method that still has a real non-test runtime consumer; record such a retained consumer in the Completion Report.

### R4 — Platform model UI is selection-only

`PlatformModelConfiguration` may keep its current component/file name, but its rendered content MUST contain only Platform model selection/status. It MUST NOT render a Catalogue administration section.

Load exactly:

```ts
Promise.all([
  listPlatformAvailableModels(),
  getPlatformAgentConfiguration(),
]);
```

Do not call `listModelCatalogue()` or a replacement global catalogue action.

The heading/copy must communicate the new ownership boundary. Use equivalent wording to:

```text
Platform model
Select the active Platform model from models made available by Admin for this environment.
```

The page SHOULD show a short informational note equivalent to:

```text
Model catalogue and availability are managed in Admin.
```

Do not invent a cross-application link unless a canonical Admin URL already exists in inspected configuration.

### R5 — Platform dropdown contains only currently Platform-available models

For each `AvailableCommerceModel` returned by `listPlatformAvailableModels()`, render one option using the Catalogue Entry ID as the value.

The human-readable option label MUST include both display name and full dynamic provider identity:

```text
<displayName> (<provider>/<providerModelId>)
```

Example:

```text
Claude Sonnet (anthropic/claude-sonnet-4.5)
```

Do not hard-code provider labels such as OpenAI/Groq.

Do not render Shop Availability models in the Platform selector.

### R6 — Platform selection uses the durable Agent Configuration model version

Use:

```text
getPlatformAgentConfiguration().modelId
getPlatformAgentConfiguration().modelEditVersion
```

as the authoritative current Platform selection/CAS state.

When the user selects a valid available model, call:

```ts
setPlatformModelSelection({
  operationId,
  reason: 'Set platform default model',
  modelId,
  expectedEditVersion: configuration?.modelEditVersion ?? 1,
});
```

Do not introduce a Platform "clear" operation in this task.

The current environment may temporarily have no Platform model selected; in that state render a non-selectable placeholder equivalent to:

```text
Select a model
```

### R7 — A broken durable Platform selection must be visible and recoverable, not silently cleared

If:

```text
configuration.modelId != NULL
AND
configuration.modelId is absent from listPlatformAvailableModels()
```

then:

1. preserve the durable `modelId`;
2. render a disabled select option with exactly that ID as its value and wording equivalent to:

```text
Current selection unavailable — <modelId>
```

3. render a visible warning (`role="alert"`) equivalent to:

```text
The selected Platform model is no longer available. Select an available model to repair this configuration.
```

4. allow `SUPER_ADMIN` to replace it with any currently Platform-available model;
5. do not call a mutation merely because the component loaded.

This UI behaviour reflects the fail-closed durable-selection semantics owned by COMMERCE-002.

### R8 — Empty Platform availability is explicit

If `listPlatformAvailableModels()` returns no models:

- render no selectable model choices;
- render status text equivalent to:

```text
No Platform models are available. Configure Model Availability in Admin.
```

- do not manufacture a default model;
- do not query the global catalogue as fallback.

### R9 — Shop model UI uses effective Shop availability only
### R9A — Shop UI must display inherited model provenance

When the Shop Agent Configuration has `modelId = NULL`, the UI MUST call/use the COMMERCE-002 effective model result for the same Shop/environment and render the inherited winner explicitly.

Render one of these states:

```text
Inherited from Price Plan — <displayName> (<provider>/<providerModelId>)
Inherited from Platform — <displayName> (<provider>/<providerModelId>)
Inherited model unavailable — <bounded reason>
```

For a Price Plan winner, show the current pricing-plan display identity when already available to the server-side view model, but do not expose or add any merchant model-selection control. The minimum required provenance is `selectionSource = PRICING_PLAN`.

The clear/null option remains a single choice. Do NOT add separate `Use Price Plan model` and `Use Platform model` choices because those are not merchant/Shop selections; they are the deterministic inheritance chain.


`ShopAgentConfiguration` MUST load model data with:

```ts
listEffectiveAvailableModels(shopId)
```

and MUST NOT call `listModelCatalogue()`.

The existing prompt/instruction calls in this component are outside this task and must retain their current/frozen behaviour.

The model dropdown begins with exactly one inheritance option equivalent to:

```text
Use platform model
```

with value:

```text
""
```

Selecting that option must continue to call `clearShopModelSelection(...)` using the current `modelEditVersion`.

### R10 — Shop options expose availability provenance

Each effective Shop option MUST use the Catalogue Entry ID as its value and include:

```text
display name
provider/providerModelId
availability provenance
```

Use deterministic labels equivalent to:

```text
<displayName> (<provider>/<providerModelId>) — Platform
<displayName> (<provider>/<providerModelId>) — Shop
```

where the suffix comes from `availableModel.availability.scope`.

Do not infer provenance from whether the selected model currently equals the Platform active model.

Do not deduplicate two distinct Catalogue Entry IDs even when they have the same `provider + providerModelId`.

### R11 — Broken explicit Shop selection is visible and recoverable

If:

```text
configuration.modelId != NULL
AND
configuration.modelId is absent from listEffectiveAvailableModels(shopId)
```

then:

1. preserve the durable Shop `modelId`;
2. render a disabled select option using that ID and wording equivalent to:

```text
Current selection unavailable — <modelId>
```

3. render a visible warning (`role="alert"`) equivalent to:

```text
The selected Shop model is no longer available. Select another available model or use the Platform model.
```

4. allow `SUPER_ADMIN` to repair it either by selecting a valid effective model or by choosing `Use inherited model`;
5. do not automatically clear the override on load.

### R12 — Server-side availability validation remains authoritative

UI option filtering is not an authorization/security mechanism.

All model selection writes continue through the COMMERCE-002 service boundary and therefore through:

```text
assertModelSelectable(...)
```

Do not duplicate the authoritative Platform/Shop availability rules in Server Actions or React.

A stale/forged model ID submitted outside the rendered option set must still be rejected by the service.

### R13 — Preserve current mutation safety and reconciliation semantics

Platform and Shop model selection must retain the existing:

```text
operationId
CAS modelEditVersion
pending/single-flight guard
UNCONFIRMED state
reconcile original operation
abandon/retry behaviour
```

Do not weaken the ARCH-021 C102 double-activation protection.

Do not generate a new operation ID during reconciliation of an unknown original operation.

### R14 — Read-only Studio role remains read-only

Current Studio authorization semantics remain:

```text
SUPER_ADMIN
    may change model selection

ADMIN
    may read model selection/availability
    may not mutate
```

Both roles see only the scoped available-model result returned by the server.

Do not expose the complete Admin catalogue to read-only Commerce Studio users.

### R15 — Update Agent Configuration copy, not ARCH-023 prompt behaviour

Update the top-level Agent Configuration lede so it no longer says Commerce Studio manages the Platform Model Catalogue.

Use wording equivalent to:

```text
Select the active CommerceAgent Platform model and optional Shop override from models made available by Admin. Shops without an override inherit their current Price Plan model when configured, otherwise the Platform model.
```

Do not remove or redesign Prompt/Instruction components in this task.

Do not alter ARCH-023 ownership or prompt/instruction semantics.

### R16 — Remove now-unused Catalogue UI/styles

After removing the Catalogue authoring UI, remove CSS selectors/components that are no longer referenced solely because of that UI, including current selectors such as:

```text
.model-catalogue-list
.model-row
```

only when a repository-wide reference search confirms no remaining consumer.

Do not perform unrelated style cleanup.

### R17 — Focused UI regression matrix is mandatory

Update/add tests proving at minimum:

#### Platform

1. the Model Catalogue heading/form/list is absent;
2. `Add model`, `Save details`, `Enable` and `Disable` Catalogue controls are absent;
3. Platform UI calls `listPlatformAvailableModels()` and never `listModelCatalogue()`;
4. only Platform-available model IDs returned by the server are rendered;
5. provider identity is rendered dynamically as `provider/providerModelId`;
6. valid selection calls `setPlatformModelSelection` with the exact current `modelEditVersion`;
7. a durable selected model absent from availability renders the unavailable sentinel + warning and is not automatically mutated;
8. an unavailable durable selection can be replaced by `SUPER_ADMIN`;
9. empty Platform availability renders the explicit Admin-configuration message;
10. `ADMIN` cannot mutate.

#### Shop

11. Shop UI calls `listEffectiveAvailableModels(shopId)` with the exact validated Shop ID;
12. it does not call/use a global catalogue list;
13. Platform and Shop availability entries are labelled with the correct provenance suffix;
14. two different Catalogue Entry IDs with the same provider/model identity remain two options;
15. selecting an available model calls `setShopModelSelection` with exact Shop ID/model ID/current `modelEditVersion`;
16. `Use inherited model` calls `clearShopModelSelection` with current `modelEditVersion`;
17. null Shop selection renders the COMMERCE-002 inherited winner as `PRICING_PLAN` or `PLATFORM`;
18. the UI does not offer separate Price Plan-vs-Platform inheritance choices;
19. a broken explicit Shop selection renders the unavailable sentinel + warning and is not automatically cleared;
20. `SUPER_ADMIN` can repair a broken selection by valid replacement or inherited Price Plan/Platform resolution;
21. existing Prompt/Instruction selection behaviour continues to pass unchanged;
22. `ADMIN` cannot mutate.

#### Server/API removal

23. `model-server-actions.ts` no longer exports Catalogue create/update/enable/global-list operations;
24. removed Catalogue mutation input types/port methods have no remaining source reference;
25. selection Server Actions still return existing typed error/reconciliation behaviour.

### R18 — No new runtime/model-provider dependency

This task MUST NOT:

```text
read CommerceOpenRouterCredential
instantiate OpenRouterModelClient
instantiate ChatOpenRouter
read COMMERCE_PREVIEW_* model/provider credentials
```

This is a Studio ownership/selection task only.

## Work Items

- [x] Replace Platform global-catalogue loading with `listPlatformAvailableModels()` + `getPlatformAgentConfiguration()`.
- [x] Remove Platform Model Catalogue create/edit/enable/disable UI.
- [x] Implement valid, unavailable and empty Platform selection states exactly as specified.
- [x] Replace Shop global-catalogue loading with `listEffectiveAvailableModels(shopId)`.
- [x] Render deterministic Platform/Shop availability provenance in Shop options.
- [x] Render the COMMERCE-002 inherited winner and `PRICING_PLAN | PLATFORM` provenance whenever Shop `modelId = NULL`; do not add separate inheritance controls.
- [x] Implement broken explicit Shop selection recovery without auto-clear.
- [x] Remove Commerce Studio global Catalogue Server Actions and mutation contracts.
- [x] Remove now-dead Catalogue service methods/compatibility aliases after reference audit.
- [x] Preserve authoritative COMMERCE-002 write-time availability validation.
- [x] Preserve single-flight/CAS/UNCONFIRMED reconciliation semantics.
- [x] Update top-level Agent Configuration wording to selection-only ownership.
- [x] Remove only now-unused Catalogue UI styles/components.
- [x] Update focused Platform/Shop/server-action tests to the R17 matrix.
- [x] Run required Validation and record exact results.

## Interfaces / Contracts

### Consumed COMMERCE-002 reads

```ts
listPlatformAvailableModels(): Promise<AvailableCommerceModel[]>;

listEffectiveAvailableModels(
  shopId: string,
): Promise<AvailableCommerceModel[]>;
```

where:

```ts
type AvailableCommerceModel = {
  availability: CommerceModelAvailability;
  model: CommerceModelCatalogueEntry;
};
```

### Platform selection state

Use the retained Agent Configuration read:

```ts
getPlatformAgentConfiguration(): Promise<AgentConfigurationState | null>;
```

and mutation:

```ts
setPlatformModelSelection({
  operationId,
  reason,
  modelId,
  expectedEditVersion,
});
```

### Shop selection state

Use:

```ts
getShopAgentConfiguration(shopId): Promise<AgentConfigurationState | null>;

setShopModelSelection({
  operationId,
  reason,
  shopId,
  modelId,
  expectedEditVersion,
});

clearShopModelSelection({
  operationId,
  reason,
  shopId,
  expectedEditVersion,
});
```

### Removed Commerce Studio Catalogue API

The following are no longer part of the Commerce Studio contract after this task:

```text
listModelCatalogue
createModelCatalogueEntry
updateModelCatalogueEntry
setModelCatalogueEnabled
```

Catalogue/Availability authoring is owned by `moda_admin`.

## Dependencies

- `ARCH-024-COMMERCE-002`
- `ARCH-024-ADMIN-002`

`ARCH-024-ADMIN-002` is a deliberate dependency: Commerce Studio must not remove its legacy Catalogue administration until the Admin-owned replacement Catalogue/Availability administration path is architect-accepted.

## Enables

None directly. COMMERCE-004 is independently gated by COMMERCE-001; Test Conversation composition does not depend on the Studio ownership-cutover UI.

## Acceptance Criteria

- [x] Commerce Studio contains no Model Catalogue create/edit/enable/disable UI.
- [x] Commerce Studio contains no Availability or OpenRouter credential administration UI.
- [x] Commerce Studio has no global `listModelCatalogue()` read boundary.
- [x] Catalogue mutation Server Actions/types/service methods used only by Commerce Studio are removed.
- [x] Platform selector receives only Platform-available models from COMMERCE-002.
- [x] Shop selector receives only Platform + exact-Shop available models from COMMERCE-002.
- [x] Platform Agent Configuration selects one Platform-available model using current CAS state.
- [x] Shop Agent Configuration selects one explicit effective model or clears to `modelId = NULL`; null renders the deterministic Price Plan -> Platform inherited winner from COMMERCE-002.
- [x] Platform and Shop invalid durable selections remain visible, fail closed, and are repairable without automatic clearing.
- [x] Shop dropdown distinguishes Platform vs Shop Availability provenance, while inherited status separately distinguishes `PRICING_PLAN` vs `PLATFORM` selection provenance.
- [x] Distinct Catalogue Entry IDs are never deduplicated by provider/model identity.
- [x] Forged/stale model IDs remain rejected server-side through `assertModelSelectable(...)`.
- [x] Existing `ADMIN` read-only / `SUPER_ADMIN` mutation authorization remains intact.
- [x] Existing single-flight, CAS and UNKNOWN-operation reconciliation semantics remain intact.
- [x] ARCH-023 Prompt/Instruction UI and semantics are unchanged.
- [x] No OpenRouter credential/runtime code is introduced.
- [x] Focused UI/server-action regressions pass.
- [x] Targeted lint/typecheck and `git diff --check` pass.

## Validation

Before Node commands:

```bash
command -v node >/dev/null 2>&1 || \
  source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"
```

Inspect `package.json` before validation and use the repository's actual scripts.

Required minimum validation:

```bash
npx vitest run \
  tests/agent-configuration-model-ui.test.tsx \
  tests/agent-configuration-shop-ui.test.tsx \
  tests/agent-configuration-server-actions.test.ts \
  tests/agent-configuration-production.test.tsx

npx eslint \
  src/studio/agent-configuration/platform-model-configuration.tsx \
  src/studio/agent-configuration/shop-agent-configuration.tsx \
  src/studio/agent-configuration/agent-configuration-screen.tsx \
  src/studio/agent-configuration/model-contracts.ts \
  src/studio/agent-configuration/model-server-actions.ts \
  src/commerce/agent-configuration/model-service.ts \
  tests/agent-configuration-model-ui.test.tsx \
  tests/agent-configuration-shop-ui.test.tsx \
  tests/agent-configuration-server-actions.test.ts \
  tests/agent-configuration-production.test.tsx

npm run typecheck

git diff --check
```

Also run bounded source-reference checks and record their output:

```bash
rg -n \
  "listModelCatalogue|createModelCatalogueEntry|updateModelCatalogueEntry|setModelCatalogueEnabled|CreateModelCatalogueEntryInput|UpdateModelCatalogueEntryInput|SetModelEnabledInput" \
  src app
```

Expected result after implementation: no runtime source references to the removed Commerce Studio Catalogue administration APIs/types.

A test-only fixture name may remain only when required to describe historical/negative compatibility and must be justified in the Completion Report.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

1. finish the Completion Report;
2. set task status to `review`;
3. return control to `moda_architect`;
4. STOP.

Do not begin any other ARCH-024 task. COMMERCE-004 has its own independent dependency on COMMERCE-001 and may already be executing separately.

## Implementation Notes

### Current inspected baseline

At task definition time, the integrated Commerce implementation includes:

```text
PlatformModelConfiguration
    listModelCatalogue()
    getPlatformModelSelection()
    createModelCatalogueEntry()
    updateModelCatalogueEntry()
    setModelCatalogueEnabled()
    setPlatformModelSelection()

ShopAgentConfiguration
    listModelCatalogue()
    getShopAgentConfiguration(shopId)
    setShopModelSelection()
    clearShopModelSelection()
```

`ARCH-024-COMMERCE-002` intentionally keeps the old Catalogue APIs only as a temporary compile bridge. This task removes that bridge after the Admin-owned replacement is accepted.

### Do not reimplement availability in React

The React components receive already-authorized/scoped available-model lists from COMMERCE-002. They must not inspect Shop IDs on arbitrary catalogue records or reconstruct effective availability themselves.

### Broken selections are durable configuration errors

An unavailable selected model is not equivalent to no selected model:

```text
Shop modelId = NULL
    intentional inherited resolution
    -> Price Plan model when configured
    -> otherwise Platform model

Shop modelId = unavailable-id
    explicit broken override
    must remain visible until repaired
    must NOT inspect/fall back to Price Plan or Platform
```

The same distinction applies to a broken Platform selected model versus no Platform selection.

## Completion Report

### Status

Ready for Architect Review (Attempt 1)

### Files Changed

`moda-interact-commerce`:

- `app/styles.css`
- `src/commerce/agent-configuration/model-service.ts`
- `src/studio/agent-configuration/agent-configuration-screen.tsx`
- `src/studio/agent-configuration/model-contracts.ts`
- `src/studio/agent-configuration/model-server-actions.ts`
- `src/studio/agent-configuration/platform-model-configuration.tsx`
- `src/studio/agent-configuration/shop-agent-configuration.tsx`
- `tests/agent-configuration-model-postgres.test.ts`
- `tests/agent-configuration-model-ui.test.tsx`
- `tests/agent-configuration-model.test.ts`
- `tests/agent-configuration-production.test.tsx`
- `tests/agent-configuration-server-actions.test.ts`
- `tests/agent-configuration-shop-ui.test.tsx`

### Work Completed

Removed Commerce Studio's global Catalogue read, Catalogue create/update/enable Server Actions, their mutation contracts, and service/port methods that existed only for Catalogue administration. Platform configuration now loads only Platform-available models plus durable Agent Configuration state; Catalogue authoring UI and its unused styles are removed. The selector displays dynamic `provider/providerModelId` identity, preserves and warns on unavailable durable IDs, and exposes explicit empty-availability state.

Shop configuration now loads effective Shop-available models for the exact validated Shop ID and renders Platform/Shop availability provenance without deduplicating distinct Catalogue Entry IDs. Clearing the override preserves the COMMERCE-002 inherited Price Plan-then-Platform result and displays its `PRICING_PLAN` or `PLATFORM` provenance; broken explicit selections remain durable and repairable. Selection mutations continue through COMMERCE-002 validation with current edit versions and existing single-flight/UNCONFIRMED reconciliation behaviour. Agent Configuration copy now describes Admin-owned availability/catalogue and the inherited selection rule. Prompt/Instruction semantics, schema, Shared package version, and provider/runtime integrations were not changed.

Implementation commit `6a7e863` (`feat(commerce): make model studio selection-only`) is pushed to `origin/task/ARCH-024-COMMERCE-003`.

### Validation Results

Passed from the dedicated Commerce implementation worktree:

- Required focused Vitest matrix: 4 files passed, 26 tests passed (`agent-configuration-model-ui`, `agent-configuration-shop-ui`, `agent-configuration-server-actions`, `agent-configuration-production`).
- Supplemental model-service regression: 1 file passed, 6 tests passed (`agent-configuration-model.test.ts`).
- Required targeted ESLint command: passed.
- `npm run typecheck` (`next typegen && tsc --noEmit`): passed.
- `git diff --check`: passed.
- Required bounded `rg` source audit over `src app`: no references to removed Catalogue operations/types.

The modified PostgreSQL proof test `tests/agent-configuration-model-postgres.test.ts` was not run because it requires an explicitly configured disposable `COMMERCE_TEST_DATABASE_URL`; the task's required Validation minimum does not require that database-backed test. The four-file UI/server-action matrix, service unit test, lint, and typecheck passed.

Launcher evidence for Attempt 1: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-024-COMMERCE-003`, branch `task/ARCH-024-COMMERCE-003`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-024-COMMERCE-003`, branch `task/ARCH-024-COMMERCE-003`. Shared workspace and shared implementation checkouts were not switched or mutated; no other task worktree was reused. Parent and implementation remote task branches were fast-forwarded `not-needed`; `origin/main` was `already-current` in both. Dependency gate passed for COMMERCE-002 and ADMIN-002. `git submodule sync --recursive` and `git submodule update --init --recursive` passed; nested Database was initialized at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`. Durable parent claim commit `792ad2c2108d782090db3a27fcea808538bc5dc1` was pushed. Implementation commit `6a7e863` was pushed to its task branch.

### Deviations

No scope deviations. PostgreSQL-backed proof was not run because its required explicit disposable database URL was unavailable; this was not part of the task's required minimum validation.

### Assumptions

Used the architect-accepted COMMERCE-002 effective model result as the authoritative source for inherited model identity and provenance; no local Price Plan/Platform resolution logic was added.

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Changes Requested — Attempt 1

### Review Notes

The implementation is otherwise architecture-conformant: Commerce Studio now consumes only scoped Platform/effective Shop availability, removes Catalogue administration APIs/UI, preserves broken durable selections for repair, displays inherited `PRICING_PLAN` / `PLATFORM` provenance, preserves COMMERCE-002 server-side selection validation and retains existing CAS/UNCONFIRMED reconciliation semantics. The recorded PostgreSQL proof-test skip is non-blocking because that test is supplemental and is not part of this task's required minimum Validation contract.

A1-R1 — Platform's `Select a model` placeholder is selectable, contrary to R6. `PlatformModelConfiguration` currently renders `<option value="">Select a model</option>` without `disabled`, while the select remains enabled for `SUPER_ADMIN`. A configured user can therefore select the blank value and invoke `setPlatformModelSelection(...)` with `modelId: ""`. R6 explicitly requires a non-selectable placeholder and states that this task must not introduce a Platform clear operation. The service rejects the empty model ID, but the UI still exposes a forbidden/invalid mutation path.

### Reviewed Files

- `moda-interact-commerce/src/studio/agent-configuration/platform-model-configuration.tsx`
- `moda-interact-commerce/src/studio/agent-configuration/shop-agent-configuration.tsx`
- `moda-interact-commerce/src/studio/agent-configuration/agent-configuration-screen.tsx`
- `moda-interact-commerce/src/studio/agent-configuration/model-contracts.ts`
- `moda-interact-commerce/src/studio/agent-configuration/model-server-actions.ts`
- `moda-interact-commerce/src/commerce/agent-configuration/model-service.ts`
- `moda-interact-commerce/tests/agent-configuration-model-ui.test.tsx`
- `moda-interact-commerce/tests/agent-configuration-shop-ui.test.tsx`
- `moda-interact-commerce/tests/agent-configuration-server-actions.test.ts`
- `moda-interact-commerce/tests/agent-configuration-production.test.tsx`
- `moda-interact-commerce/tests/agent-configuration-model.test.ts`
- `moda-interact-commerce/tests/agent-configuration-model-postgres.test.ts`

### Validation Reviewed

- Submitted focused matrix: 26 tests across the four required UI/Server Action files — passed.
- Submitted supplemental model-service suite: 6 tests — passed.
- Submitted targeted ESLint, `npm run typecheck`, `git diff --check` and obsolete Catalogue/API source audit — passed.
- Independent source audit confirms no runtime `listModelCatalogue`, Catalogue mutation action/type, Catalogue-only service method, model-provider credential, or OpenRouter runtime dependency remains in this Studio boundary.
- `@modainteract/moda-interact-shared` remains pinned to accepted `1.1.0`.
- The uploaded review archive contains no installed dependency tree, so dependency-backed Vitest/typecheck/lint commands were not independently rerun in the review environment.
- `tests/agent-configuration-model-postgres.test.ts` was not executed by the implementer because no explicit disposable `COMMERCE_TEST_DATABASE_URL` was available; this is not a required minimum validation item for COMMERCE-003.

### Architecture Conformance

Changes requested only for R6's Platform placeholder/non-clear invariant. No change is requested to COMMERCE-002 effective availability/resolution, Shop inheritance, Catalogue ownership, Prompt/Instruction semantics, database schema, Shared package version, or provider/runtime integration.

### Follow-up

A1-R1 correction contract for Attempt 2:

1. Make the Platform `Select a model` placeholder non-selectable (for example, a disabled `value=""` option) so the Platform selector cannot initiate an empty-model mutation.
2. Do not add a Platform clear Server Action, service operation, or alternate clear path.
3. Add focused regression coverage proving the placeholder is disabled/non-selectable and that the UI cannot call `setPlatformModelSelection(...)` with `modelId: ""`. Cover the configured Platform state and the empty-availability/no-selection state sufficiently to preserve the placeholder semantics.
4. Preserve all currently conformant Platform/Shop availability, inherited provenance, broken-selection repair, authorization, CAS and reconciliation behaviour.
5. Rerun the task's required Validation and return this same task to `review`. The supplemental PostgreSQL proof remains optional unless the correction changes database-backed behaviour.
6. Do not start a follow-on ARCH-024 task.
