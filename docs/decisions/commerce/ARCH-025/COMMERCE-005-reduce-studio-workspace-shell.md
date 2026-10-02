---
id: ARCH-025-COMMERCE-005
architecture_id: ARCH-025
title: Reduce StudioWorkspace to the final thin shell
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-COMMERCE-004
enables: []
created: 2026-10-02
updated: 2026-10-02
---

# Reduce StudioWorkspace to the final thin shell

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract generic Explore/Releases/Shops page/detail routing and reduce the public StudioWorkspace module to a thin compatibility shell over the accepted controller and workflow/view modules.

## Context

After COMMERCE-001..004, global orchestration, Release workflows and Shop views have stable owners. The remaining substantial code is generic page/detail routing plus the public shell, making this the terminal structural extraction for the StudioWorkspace tranche.

## Scope

Authorised implementation surface:

```text
components/studio-workspace.tsx
components/studio-workspace/studio-page-content.tsx
tests/studio-page-content.test.tsx
```

## Out of Scope

ToolEditor/ToolAuthoringScreen refactor, Agent Configuration refactor, AdminExplorer refactor, server-action changes, new router/framework, product-behaviour cleanup.

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

### R1 — generic page/detail router

Move `PageContent`, `Detail` and the thin `Discovery` wrapper into `studio-page-content.tsx`. Preserve current Explore schema guard/key, Release/Shop component selection, parent/back destinations, `DirtyNavigationGuard` behaviour, record heading/ID presentation and `StudioState` result handling.

### R2 — final shell

Reduce `components/studio-workspace.tsx` to the public prop/export boundary, accepted COMMERCE-001 controller wiring, specialised Agent Configuration/Tools early returns, shared heading/unknown-operation/loading shell and generic page/detail component. Keep `StudioPage` exported from the public file (re-exporting an internal type is acceptable).

### R3 — specialised boundaries stay explicit

Do not route `ToolAuthoringScreen` or `AgentConfigurationScreen` through `studio-page-content.tsx`. Preserve their current props and data handoff exactly, including selected Shop/authoring session and Tool initial list/detail narrowing.

### R4 — no duplicate orchestration

After extraction, the public shell and page router must consume the accepted controller/release/shop modules; they must not reimplement load/command/validation/shop logic.


## Work Items

- [ ] Extract generic PageContent/Detail/Discovery routing.
- [ ] Reduce the public StudioWorkspace source to the final thin shell.
- [ ] Add focused page-router/shell tests where existing frozen integration tests do not directly cover the boundary.
- [ ] Prove prior Commerce extracted modules and accepted source-inspection tests remain unchanged.


## Interfaces / Contracts

Final repository-internal page/detail composition contract. Public compatibility remains `StudioWorkspace` / `StudioPage` from `components/studio-workspace.tsx`.

## Dependencies

- `ARCH-025-COMMERCE-004`

## Enables

None

## Acceptance Criteria

- [ ] `StudioWorkspace` / `StudioPage` remain available from the same public module.
- [ ] Tool and Agent Configuration remain explicit early-return boundaries.
- [ ] Explore/Releases/Shops list/detail routing, loading/unknown/error presentation and dirty back-navigation remain unchanged.
- [ ] Public shell contains orchestration composition rather than duplicate domain workflows.
- [ ] Frozen 13/3/90-test assets and accepted source-inspection tests remain unchanged and pass.


## Validation

- [ ] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/studio-workspace.test.tsx':'400ce6b68cb5a9fdeecf9233bc2b3f58a42742c974da2c5b6ffd2b5a16ae44a7','tests/agent-configuration-screen-state.test.tsx':'72c71a09eaf5bdc2d79c686cf5ec43d5abfd49cfe421cadedbbe665140582b0a','tests/external-tools-ui.test.tsx':'97ffbc70e29d4ff60a48e5aabd0ff3faec6dea7984ed0f239fcb4a8fc868f4d3'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected frozen hashes.
- [ ] `npx vitest run tests/studio-page-content.test.tsx tests/studio-workspace.test.tsx tests/agent-configuration-screen-state.test.tsx tests/external-tools-ui.test.tsx tests/legacy-capability-surface.test.ts tests/arch024-preview-cleanup.test.ts` passes.
- [ ] `git diff -- components/studio-workspace/use-studio-workspace-controller.ts components/studio-workspace/release-composer.tsx components/studio-workspace/release-detail.tsx components/studio-workspace/shop-list.tsx components/studio-workspace/shop-inspector.tsx tests/legacy-capability-surface.test.ts tests/arch024-preview-cleanup.test.ts` is empty.

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
