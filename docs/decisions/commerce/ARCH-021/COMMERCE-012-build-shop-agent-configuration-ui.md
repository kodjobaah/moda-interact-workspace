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
status: ready
priority: 80
executor: null
claimed_at: null
attempt: 1
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

- [ ] Extend the dedicated Agent Configuration domain module with the selected-shop sub-surface.
- [ ] Add selected-shop effective configuration summary.
- [ ] Add shop model override set/clear controls.
- [ ] Add shop prompt lineage/draft/publish/activate controls.
- [ ] Add create-from-template flow for shop prompt drafts.
- [ ] Add independent inheritance/reset controls and source labels.
- [ ] Preserve Phase 1 `shopId` navigation semantics.
- [ ] Add focused authorization/isolation/inheritance/error-state UI tests.

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

- [ ] Selected shop shows effective model and prompt with independent PLATFORM/SHOP source labels.
- [ ] A shop may override only model, only prompt, both, or neither.
- [ ] Clearing one override preserves the other.
- [ ] Existing override replace/clear commands round-trip the service-provided `generationId` + `editVersion` CAS tokens, including a stale-generation conflict regression after clear/recreate.
- [ ] Shop prompt authoring is isolated to the exact selected shop.
- [ ] Shop prompt may start from a published platform template as an independent copy.
- [ ] Broken explicit model/prompt overrides are displayed as configuration errors rather than silently inherited values.
- [ ] ADMIN is read-only and no secret/session token is rendered.
- [ ] Shop Agent Configuration logic does not re-accumulate inside `StudioWorkspace`.
- [ ] No live model/provider execution occurs.

## Validation

- [ ] focused shop Agent Configuration UI tests
- [ ] inheritance matrix UI tests
- [ ] cross-shop isolation/auth tests
- [ ] selected-shop navigation/refresh regressions
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

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
- `src/studio/agent-configuration/agent-configuration-screen.tsx`
- `src/studio/agent-configuration/shop-agent-configuration.tsx`
- `tests/agent-configuration-production.test.tsx`
- `tests/agent-configuration-shop-ui.test.tsx`

### Work Completed

- Added the selected-shop Agent Configuration sub-surface under the dedicated domain module.
- Preserved server-validated `shopId` through the production page and workspace handoff.
- Added effective model/prompt/source/revision identity display, independent model and prompt inheritance controls, and ADMIN read-only behavior.
- Carried service-provided model/prompt `generationId` and `editVersion` CAS tokens through replace/clear operations.
- Added shop prompt draft creation, exact published-template revision copy, draft editing, publication and active-pointer clear/activate controls.
- Added dirty navigation protection and focused shop isolation/CAS/read-only UI coverage.

### Validation Results

- Launcher evidence: prepared execution was supplied with canonical parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-012`, implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-012`, synchronized task branch `task/ARCH-021-COMMERCE-012`, initialized database submodule at `98fdf715e54fe6df92ac6951facd104e410068f2`, claim commit `8d86cdd56be8eac6ec3a22d5d6135b3aa572e034`, and parent claim head `50ac184cbfe1259876299f4e8d8984cebc3a12b1`.
- VCS: implementation commit `fb5558a`; parent report commit `8507de52` before this report-only evidence update.
- `npm run test -- tests/agent-configuration-shop-ui.test.tsx tests/agent-configuration-model-ui.test.tsx tests/agent-configuration-production.test.tsx`: passed, 3 files and 8 tests.
- `npx eslint` over all changed TypeScript/TSX files: passed with no warnings.
- `git diff --check`: passed.
- `npm run typecheck`: repository baseline remains failing with 250 errors across 19 files. No diagnostics remain in the new shop component or production composition; three pre-existing diagnostics remain in `components/studio-workspace.tsx` (duplicate `productionCodePanel`, `responseProcessing` union access, and `StudioFailure.message` union access).

### Deviations

- The launcher reported `architect_review_present=true`, but the complete current task file contains `Review Status: Pending`, no review notes, and no Changes Requested items. Therefore there was no review correction checklist to apply; implementation followed the current task acceptance criteria.

### Assumptions

- Existing prompt/template server actions and resolver contracts are authoritative; no new persistence, provider, or network path was introduced.
- Template selection is resolved server-side with `selectable: true`, and only the returned published revision text/provenance is copied into a shop draft.

### Unresolved Issues

- Full repository typecheck remains blocked by the documented/pre-existing baseline diagnostics described above; this task did not alter those unrelated workspace errors.

### Architectural Concerns

None.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 establishes the dedicated selected-shop Agent Configuration surface and correctly carries the current model override `generationId` + `editVersion` tokens into model replace/clear commands. The implementation also keeps the new authoring component outside `StudioWorkspace` and preserves ADMIN server-side mutation authorization.

The shop prompt lifecycle and selected-shop boundary are not yet functionally complete:

1. `ProductionStudioPage` resolves `shopSelection` server-side but passes the raw query-string `shopId` into `StudioWorkspace`. Only `shopSelection.selectedShop?.id` (or equivalent validated server result) may enter the shop authoring surface. An unavailable/invalid query-string shop must not render or execute shop actions for that raw id.
2. `ShopAgentConfiguration.load()` returns as soon as effective resolution fails. That prevents the raw shop model selection and prompt pointer/lineage from loading, so a broken explicit override can appear as inheritance/empty state and cannot reliably be cleared. Load raw override state independently of effective resolution and render the broken explicit override as an error/recovery state rather than silently hiding it.
3. Shop prompt authoring is discoverable only through the active pointer. A newly created but not-yet-active lineage/draft disappears after `load()`/refresh, and when a new shop has no pointer the previous shop's `lineage`/`draft`/text state is not cleared. Provide a durable read of the selected shop's prompt lineage independent of the active pointer (this review explicitly authorizes a bounded read-only `getShopPrompt(shopId)`-style extension to the prompt contract/service/server action if required), and clear all shop-local editor state when shop identity changes or no lineage exists. Do not change the accepted prompt mutation semantics.
4. `createShopPrompt()` reuses one `operationId` for `CREATE_AGENT_PROMPT` and `CREATE_AGENT_PROMPT_DRAFT*`. Durable operation receipts are action/payload bound, so these must be two independently identified commands. The flow must also resume an existing shop lineage rather than attempting to recreate the one-per-shop lineage.
5. Publishing/activation currently does not represent the visible durable state correctly. `Publish revision` may run while textarea text is dirty, publishing the previously persisted draft rather than what the user is reviewing. After publication the activation button targets `activeRevision` (the revision already referenced by the pointer) and is absent when there is no pointer, so a newly published revision cannot become the shop override. Prevent publication while visible draft text is unsaved (or persist that exact text first), reconcile the returned published revision, and activate the intended newly published/selected published revision with the current pointer CAS tokens.
6. Dirty protection is only a browser `beforeunload` handler. Register the shop editor dirty state with the accepted Studio Composer navigation blocker so internal Studio/shop navigation prompts before discarding unsaved text. ADMIN must be genuinely read-only: do not leave the draft textarea editable when mutation controls are hidden.

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

### Validation Reviewed

- Submitted focused Agent Configuration validation: 3 files / 8 tests passed.
- Submitted changed-file ESLint: passed.
- Submitted `git diff --check`: passed.
- Repository-wide TypeScript baseline remains non-blocking; no new task-owned diagnostic was identified in the submitted completion report.
- Direct source review confirmed the model CAS-token handoff but exposed the prompt lifecycle/shop-isolation defects above.

### Architecture Conformance

Partial. The dedicated Agent Configuration ownership boundary and independent model override controls conform, but selected-shop validation, broken-override recovery, durable shop prompt authoring, exact visible-state publication/activation, and internal navigation dirty protection do not yet satisfy ARCH-021 / COMMERCE-012.

### Follow-up

Attempt 2 must preserve the accepted model CAS work and correct only the bounded shop-context/prompt-authoring behaviors above. Add focused regressions proving:

- invalid/unavailable raw `shopId` never enters the shop authoring surface;
- a broken explicit model or prompt override remains visible and clearable even when effective resolution returns `UNAVAILABLE`;
- a newly created unactivated shop prompt draft survives reload, while switching to another shop cannot retain or mutate the previous shop's draft;
- lineage creation and draft creation use different durable operation ids and an existing lineage is resumed rather than recreated;
- dirty visible draft text cannot be published as older persisted text, and the newly published revision can be activated when no pointer exists or can replace an existing pointer using its current `generationId` + `editVersion`;
- internal Studio/shop navigation is blocked while the prompt editor is dirty;
- ADMIN prompt editing controls are read-only;
- model and prompt clear/replace continue to round-trip service-provided generation/version tokens, including the required stale-generation conflict after clear/recreate.

Do not begin COMMERCE-013, COMMERCE-014 or Phase 3 from this task.
