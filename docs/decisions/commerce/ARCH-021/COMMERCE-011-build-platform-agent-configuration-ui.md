---
id: ARCH-021-COMMERCE-011
architecture_id: ARCH-021
title: Build platform Agent Configuration Studio surface
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-006
  - ARCH-021-COMMERCE-007
  - ARCH-021-COMMERCE-008
  - ARCH-021-COMMERCE-009
  - ARCH-021-COMMERCE-010
enables:
  - ARCH-021-COMMERCE-012
created: 2026-09-23
updated: 2026-09-23
---

# Build platform Agent Configuration Studio surface

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add a production-backed Commerce Studio Agent Configuration surface for managing the platform model catalogue/default, reusable prompt templates and the application-wide CommerceAgent prompt.

## Context

The Studio currently distributes model/prompt concerns across preview environment variables and capability authoring. Phase 2 introduces a dedicated Agent Configuration surface. This task covers platform-wide configuration only; shop overrides are a separate task.

COMMERCE-006 remains an explicit dependency because it established the accepted Phase 1 production Studio shell/workspace composition that this new surface extends. It is already architect-accepted Complete; the dependency records that baseline rather than introducing a remaining Phase 1 gate.

## Scope

- Add a clear `Agent Configuration` entry to production Studio navigation and a dedicated route/surface.
- Show the current environment as server-derived context, not a client-selectable authorization parameter.
- Model section:
  - list catalogue entries and provider/model/display/enabled state;
  - create an entry;
  - enable/disable entries;
  - select/change the platform default model with unknown/conflict reconciliation.
- Prompt-template library section:
  - list/filter/group templates and revisions by category/classification;
  - create/update display metadata/enable/disable data-driven categories such as `Clothing & Fashion`;
  - create multiple templates within a category;
  - create/edit/publish template revisions;
  - enable/disable templates.
- Platform prompt section:
  - show prompt lineage/revision history and active revision;
  - create/edit/publish a draft;
  - allow creating a draft from one exact published template revision;
  - activate a published platform prompt revision.
- Display safe stable ids/revision/source information useful for later preview validation.
- Introduce a dedicated Agent Configuration domain screen/module for model, template/category and platform-prompt state instead of adding those states/actions directly to `StudioWorkspace`.
- Keep `StudioWorkspace` as shell/navigation/orchestration for this new surface and extract only Phase-2-touched composition; do not rewrite unrelated Tools, Releases, Explore or other Studio domains.
- ADMIN remains read-only; SUPER_ADMIN gets mutation controls outside development bypass.

## Out of Scope

- Shop model/prompt override controls.
- Feature prompt removal.
- Model execution/test chat.
- Live provider calls.
- Grant/manifest/Background changes.
- Merchant access.

## Requirements

- Production composition must use the Phase 2 server ports, never fixture ports.
- Agent Configuration domain state, mutation orchestration and editor dirty/CAS handling must live outside `StudioWorkspace`; the workspace may select/render the domain surface and pass shared navigation/shop context only.
- Refactoring is incremental: do not move unrelated existing Studio domain logic solely to reduce line count.
- Template `Use` action creates/populates a prompt draft copy; the UI must not imply a live template link.
- Category display metadata may be edited, but the stable category slug/identity must not be presented as a renameable field.
- Changing model selection does not change prompt selection, and changing prompt selection does not change model selection.
- Disabled models/templates remain identifiable in historical/current state but cannot be chosen for new normal selections where the service rejects them.
- Dirty/navigation guards apply to unsaved prompt/template edits.
- Mutation UI must expose replay/conflict/unknown outcomes consistently with accepted Studio patterns.
- No provider API key or access token is rendered.

### Deterministic file boundary

Create/use these primary UI locations:

```text
app/agent-configuration/page.tsx
src/studio/agent-configuration/agent-configuration-screen.tsx
src/studio/agent-configuration/platform-agent-configuration.tsx
components/production-studio-page.tsx
components/studio-shell.tsx
components/studio-workspace.tsx
tests/agent-configuration-ui.test.tsx
```

`components/studio-workspace.tsx` may only gain the `agent-configuration` surface discriminator/render handoff and shared navigation plumbing. Model/template/prompt editor state, mutation orchestration and dirty/CAS state must live under `src/studio/agent-configuration/`. Additional helper components are permitted only under that directory. Do not opportunistically extract unrelated Tools/Releases/Explore/Features code in this task.

## Work Items

- [ ] Add production Agent Configuration route/navigation entry.
- [ ] Extract a dedicated Agent Configuration page/domain component boundary from `StudioWorkspace` for the new Phase 2 surface.
- [ ] Compose model catalogue/default UI against COMMERCE-007.
- [ ] Compose prompt-template category/library UI against COMMERCE-008, including grouped/filterable templates and category management.
- [ ] Compose platform prompt draft/history/active-pointer UI against COMMERCE-009.
- [ ] Show effective platform configuration/unavailable state from COMMERCE-010.
- [ ] Add dirty/navigation/CAS unknown-outcome handling.
- [ ] Add focused route/UI/auth tests proving production ports rather than fixtures.

## Interfaces / Contracts

Consumes:

- model configuration port from ARCH-021-COMMERCE-007;
- prompt-template port from ARCH-021-COMMERCE-008;
- prompt lifecycle port from ARCH-021-COMMERCE-009;
- effective resolver from ARCH-021-COMMERCE-010.

Produces the platform-wide Agent Configuration authoring UI used as the base for shop overrides in COMMERCE-012.

## Dependencies

- ARCH-021-COMMERCE-006
- ARCH-021-COMMERCE-007
- ARCH-021-COMMERCE-008
- ARCH-021-COMMERCE-009
- ARCH-021-COMMERCE-010

## Enables

- ARCH-021-COMMERCE-012

## Acceptance Criteria

- [ ] Production Studio exposes an Agent Configuration surface backed by real Phase 2 services.
- [ ] Platform admins can manage catalogue entries and select the platform default model.
- [ ] Platform admins can manage data-driven template categories, update their display metadata without changing stable slug/identity, and author/version multiple templates within a category.
- [ ] Platform admins can author/publish/activate the single application-wide CommerceAgent prompt lineage.
- [ ] Creating from a template copies one exact published revision and shows provenance without live linkage.
- [ ] Model and prompt controls remain independent.
- [ ] ADMIN is read-only and secrets are never rendered.
- [ ] Phase 2 Agent Configuration state/actions are not implemented inline inside `StudioWorkspace`; unrelated Studio domains are not opportunistically rewritten.
- [ ] No model/provider execution occurs.

## Validation

- [ ] focused Agent Configuration route/component tests
- [ ] model/default mutation UI tests
- [ ] template + platform prompt authoring tests
- [ ] production-port composition regression
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP.

## Implementation Notes

Do not perform a wholesale `StudioWorkspace` rewrite. Extract only the Agent Configuration boundary introduced by this task.

Do not remove the legacy capability prompt field in this task; the current ARCH-020 preview/runtime still depends on it until later ARCH-021 runtime migration. The new Agent Configuration prompt is authored in parallel but not yet consumed by the agent runtime.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

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

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
