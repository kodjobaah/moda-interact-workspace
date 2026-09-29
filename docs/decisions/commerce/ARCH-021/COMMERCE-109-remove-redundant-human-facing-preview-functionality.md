---
id: ARCH-021-COMMERCE-109
architecture_id: ARCH-021
title: Remove redundant human-facing Preview functionality
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 103
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-107
  - ARCH-021-COMMERCE-108
enables:
  - ARCH-021-GATEWAY-002
created: 2026-09-29
updated: 2026-09-29
---

# Remove redundant human-facing Preview functionality

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Delete the superseded human-facing synthetic Tool/Release/Fixture Preview composition paths after Feature-composed selected-shop Test Conversations is complete, while preserving deterministic fixture infrastructure that is still required by automated tests and External Code Response processing.

## Context

COMMERCE-105..108 establish the replacement supported flow:

```text
selected shop
 + selected Features
 + frozen effective Model/Prompt
 + every Capability under selected Features
 + exact frozen Tool revisions
 + production DefinitionExecutor
 -> multi-turn Test Conversation
```

The existing `/preview` implementation also contains older human-facing functionality:

```text
Tool source selector
Release source selector
Tool test tab
Saved selection RELEASE/DRAFT choice
Fixture scenario
Model mode
Release-composer "Test conversation" handoff
Preview-only Tool composer handoff state
synthetic-preview page copy
```

Those controls are redundant once C107/C108 are accepted. This task is intentionally subtractive.

However, not every fixture/tool-test seam is redundant. `/api/studio/preview/tool-tests` and the external preview service are also consumed by External Code Response/sample processing and deterministic automated tests. Do **not** indiscriminately delete those backend routes/services.

## Scope

Review and remove obsolete supported-human-flow code from at least:

```text
app/preview/page.tsx
src/studio/preview/preview-screen.tsx
src/studio/preview/client.ts
components/studio-workspace.tsx
components/studio-composer-context.tsx
components/preview-handoff.tsx (delete if unreferenced)
tests/preview-screen.test.tsx
tests/preview-client.test.ts
related Studio workspace/navigation tests
lib/server/config.ts old Preview fixed provider/model/key settings
```

Inspect references before deletion. A symbol/file may remain only when there is a concrete current non-human-flow consumer, and the Completion Report must name that consumer.

## Out of Scope

- Deleting deterministic Preview fixtures needed by automated tests.
- Deleting `/api/studio/preview/tool-tests` or `PreviewService.runToolTest/getToolTest` while External Code Response or other accepted internal/test consumers still use them.
- Removing external response fixture processing required by Code Response tests.
- Rewriting Feature-composed Test Conversations from C107/C108.
- Gateway/Render environment edits (GATEWAY-002).
- Background production conversation changes.
- Database migrations.

## Requirements

### R1 — `/preview` has one supported human purpose

After this task, normal Studio `/preview` is only:

```text
Feature-composed selected-shop Test Conversations
```

There must be no alternate human mode that switches the page back to Tool test, Release/DRAFT selection or fixture composition.

### R2 — remove Tool source and generic Tool-test UI state

Delete human-UI state/rendering/handlers whose only purpose is:

```text
selectedToolRevisionId
Tool source dropdown
Tool-test arguments form on /preview
Tool test tab/mode
runToolTest/getToolTest browser interaction from /preview
Tool-test polling/check UI on /preview
```

If `PreviewClient.runToolTest/getToolTest` becomes unused by browser code after this deletion, remove those methods from the **Studio browser client interface**. This does not authorize deleting the server Tool-test routes/service methods used by other consumers.

### R3 — remove Release/DRAFT composition UI and page loading

Delete normal Test Conversation dependencies on:

```text
listReleases()
listTools()
PreviewRelease / PreviewTool page props
selectedReleaseId
releaseOptions
selectionKey: release | draft
release-derived capabilityIds
release responseContract as Preview composition input
```

The Feature-based UI/server contract from C105/C107 is the only supported human composition path.

Keep normal Release authoring/activation elsewhere in Studio; this task removes only Release-as-Test-Conversation-source behaviour.

### R4 — remove human Fixture scenario and Model mode

Delete the normal UI controls/state for:

```text
Fixture scenario
modelMode FIXTURE | MODEL
fixture catalogue loading solely for Test Conversations
```

Feature Test Conversations always use the frozen selected-shop effective model from C106 and real selected-shop Tool execution from C108.

Fixture definitions/routes/service support may remain for deterministic internal/test consumers. They must not be reachable as an alternate human Test Conversations mode.

### R5 — remove release-composer Preview handoff

In Release authoring, remove the `Test conversation` action that constructs `composer.setRelease(...)` and navigates to:

```text
/preview?source=release-composer
```

Do not remove the independent Release `Edit as new release` composer state used by Release authoring/cloning.

The new Test Conversations page tests selected Features directly; a Release candidate is no longer a composition source.

### R6 — remove Preview-only composer Tool state and navigation exception

`StudioComposerContext` currently carries Preview-specific Tool handoff state and a `/preview` exception that bypasses the ordinary unsaved-navigation blocker when Tool/Release handoff refs exist.

After R5 and C107:

- remove `ToolComposerState`, `tool`, `setTool`, `toolRef` when reference search proves they are Preview-only;
- remove the `/preview` `hasPreviewHandoff` navigation exception;
- remove `releaseRef` if its only remaining use was that exception;
- retain `release`/`setRelease` if still required by Release clone/edit-as-new flow;
- delete `components/preview-handoff.tsx` if reference search shows no current supported consumer.

Do not weaken normal DirtyNavigationGuard behaviour while deleting the special case.

### R7 — remove old fixed Preview provider/model/key configuration from Commerce code

Once C106 is the only human MODEL path, remove supported runtime dependence on:

```text
COMMERCE_PREVIEW_PROVIDER
COMMERCE_PREVIEW_MODEL
COMMERCE_PREVIEW_API_KEY
```

Retain:

```text
COMMERCE_PREVIEW_ENABLED
COMMERCE_OPENAI_API_KEY
COMMERCE_GROQ_API_KEY
```

as defined by C106.

Do not edit Render Blueprints here. GATEWAY-002 owns removing/adding deployed environment wiring after this Commerce cleanup is accepted.

### R8 — preserve concrete non-human consumers

Before deleting any of these server seams, run a repository reference audit:

```text
/api/studio/preview/tool-tests
PreviewService.runToolTest
PreviewService.getToolTest
external preview service
fixture Tool execution
fixture catalogue/definitions
```

Known current non-human/internal consumers include External Code Response/sample processing and Preview test suites. Preserve the minimum backend seam needed by those consumers.

If a supposed seam is no longer referenced outside obsolete `/preview` UI after C105..108, delete it rather than retaining dead compatibility code.

The Completion Report must list every intentionally retained legacy-looking Preview seam and its actual current consumer.

### R9 — remove obsolete tests; add absence guards

Delete/rewrite tests that assert the old human UI exists.

Add explicit negative regressions proving the supported `/preview` DOM does not contain:

```text
Tool source
Release source
Tool test
Saved selection
Draft revisions
Fixture scenario
Model mode
```

Add source/reference assertions where useful to prevent reintroduction of:

```text
source=release-composer
Preview-only composer Tool handoff
COMMERCE_PREVIEW_PROVIDER
COMMERCE_PREVIEW_MODEL
COMMERCE_PREVIEW_API_KEY
```

Do not assert removal of backend fixture/tool-test symbols that remain required by the consumers documented under R8.

### R10 — materially reduce code; do not hide old UI behind flags

The completion criterion is deletion/simplification, not conditional rendering.

Do not leave the old controls behind an unused `mode` flag, query parameter or development-only switch. If functionality is no longer supported for humans, remove its UI/state wiring.

## Work Items

- [ ] Delete Tool-source/Tool-test mode from the normal Preview UI.
- [ ] Delete Release/DRAFT source selection and Tool/Release page loading from the normal Preview flow.
- [ ] Delete Fixture scenario + Model mode controls/state from the normal Preview flow.
- [ ] Remove Release composer `Test conversation` handoff to `/preview`.
- [ ] Remove Preview-only Tool composer state and the `/preview` handoff navigation exception when reference audit confirms no other consumer.
- [ ] Delete `PreviewHandoff` when unreferenced.
- [ ] Simplify the browser Preview client to the conversation operations required by C107, removing browser Tool-test methods when no browser consumer remains.
- [ ] Remove Commerce runtime/config dependence on old fixed Preview provider/model/API-key settings.
- [ ] Audit and preserve only backend fixture/tool-test seams with concrete Code Response/test consumers.
- [ ] Rewrite/remove obsolete tests and add negative old-UI/source guards.
- [ ] Record retained fixture/tool-test seams + concrete consumers in Completion Report.

## Interfaces / Contracts

Consumes the completed replacement human flow from:

```text
ARCH-021-COMMERCE-107
ARCH-021-COMMERCE-108
```

Preserves server/internal contracts only where still consumed by supported Code Response or deterministic automated-test paths.

## Dependencies

- ARCH-021-COMMERCE-107
- ARCH-021-COMMERCE-108

## Enables

- ARCH-021-GATEWAY-002

## Acceptance Criteria

- [ ] `/preview` exposes only Feature-composed selected-shop Test Conversations to humans.
- [ ] Tool source, Tool test, Release source, Release/DRAFT selection, Fixture scenario and Model mode UI/state are removed, not hidden.
- [ ] `/preview` no longer loads saved Tools/Releases as composition sources.
- [ ] Release composer no longer offers/navigates `Test conversation` to `/preview`.
- [ ] Preview-only Tool composer handoff state and `/preview` navigation bypass are removed when no longer referenced.
- [ ] `PreviewHandoff` is deleted when unreferenced.
- [ ] Browser Preview client no longer exposes unused Tool-test methods.
- [ ] Commerce code no longer depends on `COMMERCE_PREVIEW_PROVIDER`, `COMMERCE_PREVIEW_MODEL` or `COMMERCE_PREVIEW_API_KEY`.
- [ ] `COMMERCE_PREVIEW_ENABLED` and C106 provider-specific secret names remain.
- [ ] External Code Response/internal deterministic fixture Tool-test consumers remain green.
- [ ] Every retained legacy-looking Preview seam has a concrete documented consumer.
- [ ] Negative regressions prove old human controls cannot reappear accidentally.

## Validation

- [ ] Preview UI/client/page focused suites
- [ ] Studio composer/workspace/release navigation suites
- [ ] External Code Response/external preview suites that depend on Tool-test fixtures
- [ ] Preview service/route tests for retained internal fixture seams
- [ ] source/reference audit for removed Preview handoff/config symbols
- [ ] negative old-control DOM assertions
- [ ] targeted ESLint
- [ ] repository typecheck or changed-file diagnostics per baseline policy
- [ ] production build if required by repository/task-changed route composition
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not edit Gateway or begin GATEWAY-002.

## Implementation Notes

Be subtractive and reference-driven. The goal is one coherent human Test Conversations path while retaining the smallest deterministic fixture surface required by non-human consumers.

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
