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
status: review
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
