---
id: ARCH-025-COMMERCE-001
architecture_id: ARCH-025
title: Extract StudioWorkspace controller and extraction-safe source assertions
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 20
executor: copilot
claimed_at: 2026-10-02T21:04:50Z
attempt: 1
depends_on:
  - ARCH-024-COMMERCE-003
enables:
  - ARCH-025-COMMERCE-002
created: 2026-10-02
updated: 2026-10-02
---

# Extract StudioWorkspace controller and extraction-safe source assertions

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the global Studio workspace orchestration into a complete typed controller while retaining the public shell and making existing source-inspection assertions follow the bounded StudioWorkspace module set.

## Context

The current shell mixes route loading, stale-load protection, global dirty/navigation state and command admission/reconciliation with substantial page JSX. Every later Commerce task depends on one stable orchestration interface, so this task establishes that interface before presentation/workflow extraction starts.

## Scope

Authorised implementation surface:

```text
components/studio-workspace.tsx
components/studio-workspace/studio-workspace.types.ts
components/studio-workspace/use-studio-workspace-controller.ts
tests/studio-workspace-controller.test.tsx
tests/legacy-capability-surface.test.ts
tests/arch024-preview-cleanup.test.ts
```

## Out of Scope

Release Composer/Detail extraction, Shop view extraction, generic page-router extraction, Tool/Agent Configuration implementation changes, server-action changes or persistence changes.

## Requirements

### Common ARCH-025 StudioWorkspace invariants

- This is a **move-only structural refactor**. Do not change Studio product behaviour, server-action signatures/authorization, persistence semantics, Tool authoring, Agent Configuration, Discovery, Test Conversations/Preview or Shop execution contracts.
- Preserve `StudioWorkspace` and the `StudioPage` type at `components/studio-workspace.tsx`. Existing production callers/browser-evidence fixtures do not migrate.
- Preserve route identity as `page:detailId:revisionId:authoringSessionId`, while the page/detail load effect continues to trigger only from `page`, `detailId` and `revisionId`; changing only `authoringSessionId` must not add a Studio data load.
- Preserve one-time `initialResult`/`initialDetail` hydration suppression through the hydrated route identity and monotonic `loadToken` stale-result rejection.
- Preserve current page-load/provider cardinality/order: Tool list/detail, Explore schema, Release list/detail and Shop list/detail calls must not be added, removed, merged or reordered as incidental cleanup. Agent Configuration still performs no Studio list/detail server action and sets the bounded local loaded state.
- Preserve write single-flight through the current pending ref/token semantics. A second write is not admitted while one is pending; an `unknown` outcome stores the original operation ID, label, run callback, admitted content revision and optional success callback for reconciliation.
- Preserve the current operation-ID format (`c` + base36 `Date.now()` + 18 hex-like UUID characters with hyphens removed) everywhere it is used, including Release edit-as-new handoff.
- Preserve content-revision dirty fencing: `setDirty(true)` increments the content revision; a successful command clears dirty only when the submitted revision still equals the current revision.
- Preserve Studio composer navigation blocking: dirty Agent Configuration state, unconfirmed Agent Configuration operations and unknown workspace operations continue to participate in the existing blocker/lock semantics.
- Preserve specialised early-return boundaries: `AgentConfigurationScreen` and `ToolAuthoringScreen` remain outside the generic `<main>` page/detail router and retain their current props/data handoff.
- Preserve `StudioComposerContext`, `DirtyNavigationGuard`, `StudioState`, `ToolAuthoringScreen`, `AgentConfigurationScreen`, `AdminExplorer` and `src/studio/server-actions.ts` as canonical existing owners. Do not create a new router, plugin framework, command bus, state store or DI framework.
- Preserve exact current strings/routes/role gates and current source quirks during extraction. Do not opportunistically redesign Shop search/Preview/Test links, dirty clearing, validation messages or confirmation behaviour.
- These tests are frozen byte-for-byte throughout COMMERCE-001..005: `tests/studio-workspace.test.tsx` (`400ce6b68cb5a9fdeecf9233bc2b3f58a42742c974da2c5b6ffd2b5a16ae44a7`, 13 tests), `tests/agent-configuration-screen-state.test.tsx` (`72c71a09eaf5bdc2d79c686cf5ec43d5abfd49cfe421cadedbbe665140582b0a`, 3 tests), `tests/external-tools-ui.test.tsx` (`97ffbc70e29d4ff60a48e5aabd0ff3faec6dea7984ed0f239fcb4a8fc868f4d3`, 90 tests).
- `tests/legacy-capability-surface.test.ts` and `tests/arch024-preview-cleanup.test.ts` may be changed only by COMMERCE-001 and only to make their source loader follow the bounded StudioWorkspace module set without deleting/weakening existing assertions. COMMERCE-002..005 must not modify the accepted COMMERCE-001 versions.
- No ARCH-025 Commerce task may modify the adjacent canonical owner files listed in the parent regression baseline except for import-only changes explicitly authorised by that task.
- Keep tests honest: no skipped/only/todo tests, weakened expectations or new behavioural expectations merely to accommodate extraction.

### R1 — complete workspace controller contract

Create an internal typed/controller boundary that owns route identity, result/detail/loaded identity, hydration suppression, load token, global message/pending/dirty state, Agent Configuration dirty/unconfirmed state, unknown-operation state, completion token, content revision, navigation-blocker registration, `load`, `runCommand` and `reconcile`. The accepted controller must expose every global value/action consumed by COMMERCE-002..005; later tasks are consume-only. If a later task discovers a missing controller interface, it must stop and return to `moda_architect` rather than silently extending the controller.

### R2 — route/load semantics

Preserve the exact current route/load behaviour. `routeIdentity` includes `authoringSessionId`; the load effect dependencies remain `page`, `detailId`, `revisionId`. Initial hydrated identity suppresses one duplicate load. `loadToken` prevents stale list/detail results from overwriting newer route data. `agent-configuration` sets the bounded local result/detail/loaded identity without a Studio server action. Tools/Explore/Releases/Shops retain the current list/detail call selection/order.

### R3 — command/unknown reconciliation

Preserve `pendingRef` admission, completion token, unexpected thrown-failure classification, unknown-operation storage and reconciliation of the **original** operation ID/run callback/admitted revision. Preserve the exact operation-ID generator and expose it as a repository-internal helper usable by later Release Detail extraction.

### R4 — extraction-safe source inspection

Change only source-loading mechanics in `legacy-capability-surface.test.ts` and `arch024-preview-cleanup.test.ts` so the existing assertions scan `components/studio-workspace.tsx` plus direct `.ts`/`.tsx` modules under `components/studio-workspace/` in deterministic order, while retaining `studio-composer-context.tsx` in the ARCH-024 human-handoff scan. Do not remove or weaken legacy-token/obsolete-Preview assertions.

### R5 — focused controller tests

Add focused tests proving hydration suppression, stale-load rejection, no reload on authoring-session-only change, single-flight/unknown-operation admission, reconciliation with the original operation ID and content-revision dirty fencing.

### R6 — preserve current cross-route/global-state asymmetries

Do not introduce route-change resets that do not exist today. In particular, route changes must not opportunistically clear `message`, global `dirty`, Agent Configuration dirty/unconfirmed state or an unresolved `unknown` operation. Preserve the current global navigation-blocker `onDiscard` behaviour, which clears only the workspace `dirty` flag; Agent Configuration owns its own dirty/unconfirmed convergence. Existing 13/3/90-test assets remain unchanged.


## Work Items

- [ ] Introduce `studio-workspace.types.ts` and `use-studio-workspace-controller.ts` with the complete downstream contract.
- [ ] Rewire the existing monolithic shell/pages to consume the controller without moving Release/page JSX yet.
- [ ] Add focused controller tests.
- [ ] Make the two source-inspection harnesses extraction-safe without changing their assertions.
- [ ] Prove all frozen integration/state assets remain byte-identical.


## Interfaces / Contracts

Internal Commerce UI controller/type contract only. `components/studio-workspace.tsx` remains the public compatibility boundary; no cross-repository contract is introduced.

## Dependencies

- `ARCH-024-COMMERCE-003` — Complete and integrated; establishes the final Studio model-selection shape before this high-churn component is structurally extracted.

## Enables

- `ARCH-025-COMMERCE-002`

## Acceptance Criteria

- [ ] Existing production callers continue importing `StudioWorkspace` / `StudioPage` from `components/studio-workspace.tsx`.
- [ ] Route/hydration/load and write/unknown reconciliation behaviour is unchanged.
- [ ] Controller contract is sufficient for COMMERCE-002..005 without later controller redesign.
- [ ] Source-inspection assertions cover the bounded extracted module set and retain every current assertion.
- [ ] Frozen 13/3/90-test assets are unchanged and pass.


## Validation

- [ ] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/studio-workspace.test.tsx':'400ce6b68cb5a9fdeecf9233bc2b3f58a42742c974da2c5b6ffd2b5a16ae44a7','tests/agent-configuration-screen-state.test.tsx':'72c71a09eaf5bdc2d79c686cf5ec43d5abfd49cfe421cadedbbe665140582b0a','tests/external-tools-ui.test.tsx':'97ffbc70e29d4ff60a48e5aabd0ff3faec6dea7984ed0f239fcb4a8fc868f4d3'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected frozen hashes.
- [ ] `npx vitest run tests/studio-workspace-controller.test.tsx tests/studio-workspace.test.tsx tests/agent-configuration-screen-state.test.tsx tests/external-tools-ui.test.tsx tests/legacy-capability-surface.test.ts tests/arch024-preview-cleanup.test.ts` passes.

- [ ] `npm test` passes without task-introduced regression.
- [ ] `npm run typecheck` passes.
- [ ] targeted `npm run lint -- <changed Commerce source/test files>` (or repository-equivalent targeted ESLint invocation using the declared lint script) passes.
- [ ] `npm run build` succeeds.
- [ ] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Commerce task.

## Implementation Notes

None

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

Pending.

### Follow-up

None
