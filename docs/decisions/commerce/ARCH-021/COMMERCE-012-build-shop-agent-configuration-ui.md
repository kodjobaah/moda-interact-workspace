---
id: ARCH-021-COMMERCE-012
architecture_id: ARCH-021
title: Build shop Agent Configuration override surface
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 80
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-021-COMMERCE-004
  - ARCH-021-COMMERCE-007
  - ARCH-021-COMMERCE-008
  - ARCH-021-COMMERCE-009
  - ARCH-021-COMMERCE-010
  - ARCH-021-COMMERCE-011
enables: []
created: 2026-09-23
updated: 2026-09-23
---

# Build shop Agent Configuration override surface

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Extend Agent Configuration so a platform admin can inspect effective configuration for the selected shop and independently manage that shop's model override and behavioural prompt override.

## Context

Phase 1 established server-validated `shopId` navigation context. Phase 2 now uses that context to configure one shop without making model/prompt feature-specific. Shop model and prompt fallback are independent, and removing an override returns only that dimension to platform inheritance.

## Scope

- Reuse the existing server-validated selected-shop Studio context.
- Show the selected shop's effective model and source (`PLATFORM` or `SHOP`).
- Allow SUPER_ADMIN to set/replace/clear the shop model override from enabled catalogue entries.
- Show the selected shop's effective prompt and source (`PLATFORM` or `SHOP`).
- Allow SUPER_ADMIN to create/edit/publish the shop prompt lineage and set/replace/clear its active override.
- Allow a shop prompt draft to be created from one exact published application-wide template revision.
- Clearly show inheritance when no override exists.
- Clearly show configuration error state when an explicit override is broken/disabled; do not present it as inherited.
- Preserve selected `shopId` across Agent Configuration navigation/refresh using the accepted Phase 1 mechanism.
- Extend the dedicated Agent Configuration domain component/module created by COMMERCE-011; do not add shop prompt/model editor state back into `StudioWorkspace`.
- ADMIN remains read-only.

## Out of Scope

- Merchant authentication/authorization.
- Merchant-owned prompt templates.
- Entitlement/tier policy for model overrides.
- Live chat/model execution.
- Grant/manifest/Background changes.
- Feature prompt removal.

## Requirements

- Model and prompt override actions are independent.
- `Clear model override` must not change prompt state.
- `Clear prompt override` must not change model state.
- Shop prompt operations must be scoped to the exact server-validated shop; a browser-supplied shop id must never bypass authorization/validation.
- A template creates a copied shop prompt draft; later template edits do not affect it.
- The UI must display effective ids/revisions/source so later preview work can prove what will be frozen.
- `StudioWorkspace` remains orchestration/navigation only for this surface; selected-shop authoring logic belongs to the Agent Configuration domain module.
- Broken explicit override state must remain visible and fail closed through the resolver.
- When an explicit shop model/prompt override exists, the UI must carry the opaque `generationId` and `editVersion` returned by the owning service and submit both on replace/clear. It must never synthesise/reset generation tokens client-side.

### Deterministic file boundary

Extend the Agent Configuration module created by COMMERCE-011; do not create a second shop-settings implementation elsewhere.

Primary locations:

```text
src/studio/agent-configuration/agent-configuration-screen.tsx
src/studio/agent-configuration/shop-agent-configuration.tsx
app/agent-configuration/page.tsx
components/studio-workspace.tsx          # navigation/shop-context handoff only
tests/agent-configuration-shop-ui.test.tsx
```

Use the existing Phase 1 `shopId` query/navigation contract and `ShopExecutionContext`. Do not introduce another selected-shop store, cookie, localStorage key or database preference. Shop override editor state remains under `src/studio/agent-configuration/`.

## Work Items

- [x] Extend the dedicated Agent Configuration domain module with the selected-shop sub-surface.
- [x] Add selected-shop effective configuration summary.
- [x] Add shop model override set/clear controls.
- [x] Add shop prompt lineage/draft/publish/activate controls.
- [x] Add create-from-template flow for shop prompt drafts.
- [x] Add independent inheritance/reset controls and source labels.
- [x] Preserve Phase 1 `shopId` navigation semantics.
- [x] Add focused authorization/isolation/inheritance/error-state UI tests.

## Interfaces / Contracts

Consumes:

- selected-shop context from ARCH-021-COMMERCE-004;
- model configuration port from ARCH-021-COMMERCE-007 for shop model set/clear;
- prompt-template port from ARCH-021-COMMERCE-008 for selectable template discovery;
- prompt lifecycle port from ARCH-021-COMMERCE-009 for shop prompt draft/publish/active-pointer operations;
- effective configuration resolver from ARCH-021-COMMERCE-010;
- platform Agent Configuration domain surface from ARCH-021-COMMERCE-011 as the UI/module base.

Produces the selected-shop model/prompt override sub-surface within the shared Agent Configuration module. Platform template-library and platform prompt authoring remain independently owned by COMMERCE-013 and COMMERCE-014.

## Dependencies

- ARCH-021-COMMERCE-004
- ARCH-021-COMMERCE-007
- ARCH-021-COMMERCE-008
- ARCH-021-COMMERCE-009
- ARCH-021-COMMERCE-010
- ARCH-021-COMMERCE-011

## Enables

None. COMMERCE-013 and COMMERCE-014 are independent Phase 2 UI tasks and may still be incomplete when this task finishes.

## Acceptance Criteria

- [x] Selected shop shows effective model and prompt with independent PLATFORM/SHOP source labels.
- [x] A shop may override only model, only prompt, both, or neither.
- [x] Clearing one override preserves the other.
- [x] Existing override replace/clear commands round-trip the service-provided `generationId` + `editVersion` CAS tokens, including a stale-generation conflict regression after clear/recreate.
- [x] Shop prompt authoring is isolated to the exact selected shop.
- [x] Shop prompt may start from a published platform template as an independent copy.
- [x] Broken explicit model/prompt overrides are displayed as configuration errors rather than silently inherited values.
- [x] ADMIN is read-only and no secret/session token is rendered.
- [x] Shop Agent Configuration logic does not re-accumulate inside `StudioWorkspace`.
- [x] No live model/provider execution occurs.

## Validation

- [x] focused shop Agent Configuration UI tests
- [x] inheritance matrix UI tests
- [x] cross-shop isolation/auth tests
- [x] selected-shop navigation/refresh regressions
- [x] targeted lint/typecheck
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin COMMERCE-013, COMMERCE-014 or Phase 3.

## Implementation Notes

Use the existing selected-shop context; do not introduce a second independent shop selector. The future merchant-facing Studio will replace platform-admin shop selection with merchant authorization but should reuse the same shop-scoped configuration service boundary.

## Completion Report

### Status

Ready for Review

### Files Changed

- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `src/commerce/agent-configuration/prompt-service.ts`
- `src/studio/agent-configuration/agent-configuration-screen.tsx`
- `src/studio/agent-configuration/prompt-contracts.ts`
- `src/studio/agent-configuration/prompt-server-actions.ts`
- `src/studio/agent-configuration/shop-agent-configuration.tsx`
- `tests/agent-configuration-production.test.tsx`
- `tests/agent-configuration-shop-ui.test.tsx`

### Work Completed

- Added the selected-shop Agent Configuration sub-surface under the dedicated domain module.
- Preserved server-validated `shopId` by forwarding only `shopSelection.selectedShop?.id`; unavailable or invalid query-string shops never enter the authoring surface.
- Loaded model/pointer/lineage raw state independently of effective resolution, keeping broken explicit overrides visible and clearable as configuration errors.
- Added the durable `getShopPrompt(shopId)` read so unactivated shop lineages and drafts survive refresh and shop changes clear stale local editor state.
- Resumed an existing shop lineage and allocated independent operation IDs for lineage creation and draft creation; template copies remain exact and independent.
- Reconciled publish results and activated the returned published revision using current pointer generation/edit CAS tokens; publication is disabled while visible text is dirty.
- Connected shop editor dirty state to the accepted Studio Composer navigation blocker, made ADMIN prompt text read-only, and retained model/prompt independent CAS replace/clear semantics.

### Validation Results

- Launcher evidence: prepared execution was supplied with canonical parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-012`, implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-012`, synchronized task branch `task/ARCH-021-COMMERCE-012`, initialized database submodule at `98fdf715e54fe6df92ac6951facd104e410068f2`, claim commit `3b642241d94ac77854d5a82904735d676883070c`, parent head `b0ce775f2d36f68c511336f9b0a9684324ae7bc2`, and implementation head `fb5558ab454070c879454a86d2f659e9e35c58ab` at handoff.
- VCS: implementation correction commit `f252484` pushed to `origin/task/ARCH-021-COMMERCE-012`; parent report commit follows this update.
- Focused Attempt 2 validation: `npm run test -- tests/agent-configuration-shop-ui.test.tsx tests/agent-configuration-production.test.tsx tests/agent-configuration-prompts.test.ts`: passed, 3 files and 11 tests.
- Broader targeted validation: 7 of 8 selected files passed, 30 tests passed. The existing `tests/agent-configuration-effective.test.ts` mock path remains failing 9 tests because its Prisma mock exposes no `Prisma.TransactionIsolationLevel.RepeatableRead`; this is the documented baseline incompatibility and is outside the changed behavior.
- `npx eslint` over all changed TypeScript/TSX files: passed with no warnings.
- `git diff --check`: passed.
- `npm run typecheck`: exit 2 with 248 errors across 18 files. Changed-file diagnostics are limited to the pre-existing three `components/studio-workspace.tsx` errors (duplicate `productionCodePanel`, `responseProcessing` union access, and `StudioFailure.message` union access) plus four pre-existing generated-client/type diagnostics in `src/commerce/agent-configuration/prompt-service.ts`; no diagnostics remain in the new Agent Configuration screen/contracts or focused tests.

### Correction Checklist

- [x] Validated shop boundary: `components/production-studio-page.tsx` forwards only `shopSelection.selectedShop?.id`; `tests/agent-configuration-production.test.tsx` proves unavailable raw IDs are suppressed.
- [x] Broken override recovery: `shop-agent-configuration.tsx` loads raw model/pointer/lineage state alongside effective resolution; focused UI coverage proves a disabled model remains clearable with its service CAS tokens.
- [x] Durable lineage and isolation: `prompt-contracts.ts`, `prompt-server-actions.ts`, and `prompt-service.ts` add `getShopPrompt`; the component clears shop-local state on identity/load changes and resumes existing lineages; tests cover distinct operation IDs and no duplicate lineage creation.
- [x] Publication/activation: the component blocks publication while visible text is dirty, publishes the current draft, and activates the returned revision with current pointer CAS; focused UI coverage proves the no-pointer activation path.
- [x] Composer dirty guard and ADMIN read-only: `agent-configuration-screen.tsx`/`studio-workspace.tsx` pass accepted Composer dirty state; the editor is read-only for ADMIN and the focused UI test covers it.
- [x] Accepted model CAS behavior preserved: existing model controls remain unchanged; focused UI coverage continues to verify generation/edit token round-trip.

### Deviations

- The locked dependency tree was restored with `npm ci` because the prepared worktree had an incomplete `node_modules` tree and could not resolve the declared Vitest binary. The install emitted existing peer/engine/deprecation warnings and did not modify tracked files.

### Assumptions

- Existing prompt/template server actions and resolver contracts are authoritative; no new persistence, provider, or network path was introduced.
- Template selection is resolved server-side with `selectable: true`, and only the returned published revision text/provenance is copied into a shop draft.

### Unresolved Issues

- Full repository typecheck remains blocked by 248 documented/pre-existing baseline diagnostics described above; no new focused-file diagnostics remain.
- The broader effective-configuration test mock still requires the generated Prisma enum surface and remains a baseline test-environment failure; it was not changed because it is outside this bounded UI correction.

### Architectural Concerns

None.

### Attempt 3 Rework

#### Status

Ready for Review

#### Corrections Completed

- Added a monotonic load-generation guard so a slower prior-shop request cannot repopulate the selected shop's model, pointer, lineage, or draft state.
- Blocked model mutations, prompt inheritance clearing, and new draft creation while visible prompt text is dirty; existing durable DRAFTs are resumed instead of duplicated.
- Reconciled the lineage and pointer after publication succeeds but activation loses CAS, exposing the immutable published revision without republishing it.
- Preserved effective-resolution error messages while raw broken override state remains loaded and clearable.
- Added focused regressions for stale-shop loads, dirty independent mutations, duplicate-draft prevention, publish/activation recovery, and visible resolver errors.

#### Launcher and VCS Evidence

- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-012`
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-012`
- Branch: `task/ARCH-021-COMMERCE-012`
- Attempt 3 claim commit: `e3bff01013e10f0c210025b76c9acbcc495b94c5`
- Parent synchronization merge: `d81b725d`
- Implementation synchronization merge: `72909d4`
- Attempt 3 implementation correction commit: `2345baa`
- Recursive database submodule: `98fdf715e54fe6df92ac6951facd104e410068f2`

#### Validation Results

- PASS: focused shop UI suite - 11 tests passed.
- PASS: combined focused suite (`agent-configuration-shop-ui`, production composition, platform prompt UI, prompt service, and prompt server actions) - 5 files, 27 tests passed.
- PASS: targeted ESLint over all task-touched implementation and test files.
- PASS: changed-file diagnostics reported no errors.
- PASS: `git diff --check`.
- The implementation worktree dependencies were removed by a separate disk-cleanup command after validation; no tracked files were affected.

#### Remaining Baseline

The repository-wide typecheck and the previously documented unrelated Prisma mock/type diagnostics remain outside this bounded UI correction. No focused failures or changed-file diagnostics remain.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 3 is architect-accepted. The bounded UI-state correction closes every item from the prior review while preserving the accepted COMMERCE-007/009 model/prompt CAS and durable replay boundaries.

- Shop-context isolation now uses a monotonically increasing load generation. A slower response from a previously selected shop is ignored and cannot repopulate model, pointer, lineage, draft or editor state after the shop changes.
- Dirty prompt text now blocks independent model changes, prompt inheritance clearing and new-draft/reload paths that would replace the editor. Successful unrelated mutations can no longer silently discard the visible prompt draft.
- Existing durable DRAFT revisions are resumed instead of creating a second DRAFT for the same lineage.
- Publish success followed by pointer activation failure reloads durable lineage and pointer state. The immutable PUBLISHED revision becomes visible for a later activation attempt and publication is not retried.
- Effective-resolution failures remain visibly reported while raw model/prompt override state is still loaded and clearable.
- The server-validated selected shop, ADMIN read-only boundary, exact template copy, separate durable operation ids, Composer navigation dirty guard and generation/edit CAS token round-trip remain intact.

No live provider/model execution, grant/manifest mutation or cross-service contract change is introduced by this task.

### Reviewed Files

- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `src/studio/agent-configuration/agent-configuration-screen.tsx`
- `src/studio/agent-configuration/shop-agent-configuration.tsx`
- `src/studio/agent-configuration/prompt-contracts.ts`
- `src/studio/agent-configuration/prompt-server-actions.ts`
- `src/commerce/agent-configuration/prompt-service.ts`
- `tests/agent-configuration-shop-ui.test.tsx`
- `tests/agent-configuration-production.test.tsx`
- `tests/agent-configuration-prompts.test.ts`

### Validation Reviewed

- Attempt 3 focused shop UI suite: 11 tests passed.
- Attempt 3 combined focused suite: 5 files / 27 tests passed.
- Targeted ESLint over task-touched implementation and test files: passed.
- Changed-file diagnostics: passed.
- `git diff --check`: passed.
- Repository-wide TypeScript baseline remains non-blocking; no new task-owned diagnostic is reported.
- Direct source review confirms the five Attempt 3 correction requirements are implemented and the accepted service-side CAS/replay semantics remain unchanged.

### Architecture Conformance

Conforms. The selected-shop Agent Configuration surface now preserves the server-validated shop boundary across asynchronous loads, protects unsaved prompt state from independent mutations, resumes one durable DRAFT, reconciles publish/activation partial success, preserves resolver errors, round-trips opaque generation/edit CAS tokens and remains read-only for ADMIN. Model and prompt overrides remain independent and no execution/provider boundary is crossed.

### Follow-up

None for COMMERCE-012. The task is Complete. It has no dependants to promote. Preserve newer parallel-branch architect state for COMMERCE-013 when reconciling parent branches.
