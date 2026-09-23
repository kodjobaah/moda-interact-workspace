---
id: ARCH-021-COMMERCE-011
architecture_id: ARCH-021
title: Build Agent Configuration shell and platform model UI
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 70
executor: copilot
claimed_at: 2026-09-23T17:14:41Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-006
  - ARCH-021-COMMERCE-007
enables:
  - ARCH-021-COMMERCE-012
  - ARCH-021-COMMERCE-013
  - ARCH-021-COMMERCE-014
created: 2026-09-23
updated: 2026-09-23
---

# Build Agent Configuration shell and platform model UI

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Create the dedicated production Agent Configuration Studio route/module and implement the platform model-catalogue/default-model UI against the accepted model configuration service.

## Context

Phase 2 introduces Agent Configuration as a dedicated Studio domain. The previous COMMERCE-011 definition bundled model management, prompt-template management and platform prompt authoring into one UI task even though those are independently useful capabilities with different service dependencies. This task establishes only the shared Agent Configuration shell plus the platform model surface. Template and prompt authoring are separate COMMERCE-013/014 tasks; shop overrides remain COMMERCE-012.

COMMERCE-006 remains an explicit dependency because it established the accepted Phase 1 production Studio shell/workspace composition extended by this route.

## Scope

- Add a clear `Agent Configuration` entry to production Studio navigation and a dedicated route/surface.
- Show the current environment as server-derived context, not a client-selectable authorization parameter.
- Establish the dedicated Agent Configuration domain screen/module used by later Phase 2 UI tasks.
- Model section only:
  - list catalogue entries and provider/model/display/enabled state;
  - create an entry;
  - update mutable display metadata;
  - enable/disable entries;
  - select/change the platform default model with accepted replay/conflict/unknown-outcome reconciliation.
- Display safe stable model ids/provider model ids useful for later preview validation.
- Keep `StudioWorkspace` as shell/navigation/orchestration only for this surface.
- ADMIN remains read-only; SUPER_ADMIN gets mutation controls outside development bypass.

## Out of Scope

- Prompt-template category/library UI; owned by ARCH-021-COMMERCE-013.
- Platform prompt authoring/history/activation UI; owned by ARCH-021-COMMERCE-014.
- Shop model/prompt override controls; owned by ARCH-021-COMMERCE-012.
- Feature prompt removal.
- Model execution/test chat.
- Live provider calls.
- Grant/manifest/Background changes.
- Merchant access.

## Requirements

- Production composition must use the COMMERCE-007 production server port, never fixture ports.
- Agent Configuration domain state, mutation orchestration and model dirty/CAS handling must live outside `StudioWorkspace`; the workspace may select/render the domain surface and pass shared navigation/shop context only.
- Refactoring is incremental: do not move unrelated existing Studio domain logic solely to reduce line count.
- Disabled models remain identifiable in current/historical state but cannot be chosen for new selections where COMMERCE-007 rejects them.
- Mutation UI must surface accepted replay/conflict/unknown outcomes without inventing another mutation state model.
- No provider API key, access token or secret configuration is rendered.

### Deterministic file boundary

Create/use these primary UI locations:

```text
app/agent-configuration/page.tsx
src/studio/agent-configuration/agent-configuration-screen.tsx
src/studio/agent-configuration/platform-model-configuration.tsx
components/production-studio-page.tsx
components/studio-shell.tsx
components/studio-workspace.tsx
tests/agent-configuration-model-ui.test.tsx
```

`components/studio-workspace.tsx` may only gain the `agent-configuration` surface discriminator/render handoff and shared navigation plumbing. Model editor state and mutation orchestration must live under `src/studio/agent-configuration/`. Additional helper components are permitted only under that directory. Do not opportunistically extract unrelated Tools/Releases/Explore/Features code.

## Work Items

- [ ] Add production Agent Configuration route/navigation entry.
- [ ] Establish the dedicated Agent Configuration page/domain component boundary outside `StudioWorkspace`.
- [ ] Compose model catalogue/default UI against COMMERCE-007.
- [ ] Add accepted replay/conflict/unknown-outcome presentation for model mutations.
- [ ] Add focused route/UI/auth tests proving production ports rather than fixtures.

## Interfaces / Contracts

Consumes:

- model configuration port from ARCH-021-COMMERCE-007;
- accepted production Studio shell composition from ARCH-021-COMMERCE-006.

Produces the shared Agent Configuration UI/module shell and platform model surface that COMMERCE-012, COMMERCE-013 and COMMERCE-014 extend.

## Dependencies

- ARCH-021-COMMERCE-006
- ARCH-021-COMMERCE-007

## Enables

- ARCH-021-COMMERCE-012
- ARCH-021-COMMERCE-013
- ARCH-021-COMMERCE-014

## Acceptance Criteria

- [ ] Production Studio exposes an Agent Configuration surface backed by the real COMMERCE-007 model service.
- [ ] Platform admins can list/create/update/enable/disable catalogue entries and select the platform default model.
- [ ] ADMIN is read-only and secrets are never rendered.
- [ ] Model mutation replay/conflict/unknown outcomes use accepted Studio behaviour.
- [ ] Agent Configuration state/actions are not implemented inline inside `StudioWorkspace`; unrelated Studio domains are not opportunistically rewritten.
- [ ] No prompt/template authoring or model/provider execution is introduced.

## Validation

- [ ] focused Agent Configuration route/component tests
- [ ] model/default mutation UI tests
- [ ] production-port composition regression
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin COMMERCE-012, COMMERCE-013 or COMMERCE-014.

## Implementation Notes

Do not perform a wholesale `StudioWorkspace` rewrite. Extract only the Agent Configuration shell/model boundary introduced by this task.

Do not remove the legacy capability prompt field in this task; the current ARCH-020 preview/runtime still depends on it until later ARCH-021 runtime migration.

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
