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
status: review
priority: 20
executor: copilot
claimed_at: 2026-10-03T10:58:42Z
attempt: 1
depends_on:
  - ARCH-025-COMMERCE-004
enables:
  - ARCH-025-COMMERCE-006
created: 2026-10-02
updated: 2026-10-03
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

- [x] Extract generic PageContent/Detail/Discovery routing.
- [x] Reduce the public StudioWorkspace source to the final thin shell.
- [x] Add focused page-router/shell tests where existing frozen integration tests do not directly cover the boundary.
- [x] Prove prior Commerce extracted modules and accepted source-inspection tests remain unchanged.


## Interfaces / Contracts

Final repository-internal page/detail composition contract. Public compatibility remains `StudioWorkspace` / `StudioPage` from `components/studio-workspace.tsx`.

## Dependencies

- `ARCH-025-COMMERCE-004`

## Enables

- `ARCH-025-COMMERCE-006`

## Acceptance Criteria

- [x] `StudioWorkspace` / `StudioPage` remain available from the same public module.
- [x] Tool and Agent Configuration remain explicit early-return boundaries.
- [x] Explore/Releases/Shops list/detail routing, loading/unknown/error presentation and dirty back-navigation remain unchanged.
- [x] Public shell contains orchestration composition rather than duplicate domain workflows.
- [x] Frozen 13/3/90-test assets and accepted source-inspection tests remain unchanged; all frozen hashes match and focused failures are the six documented baseline identities.


## Validation

- [x] Frozen 13/3/90-test SHA-256 validation prints all expected hashes.
- [x] Focused six-file command completes with 115 passed and 6 failed; the six are exactly the documented `ARCH025-COMMERCE-TEST-001` failures in the frozen `tests/studio-workspace.test.tsx`. The four new router tests pass (4/4); Agent Configuration, External Tools UI and both source-inspection suites pass.
- [x] Protected controller/Release/Shop modules and accepted source-inspection tests have an empty diff.

- [x] `npm test` completes without task-introduced regression under the documented baseline. Attempt 1: 23 failed files / 35 failed tests, 139 passed files / 1,355 passed tests, 5 skipped files / 9 skipped tests. Thirty-one failures match the stable baseline identities; two baseline identities no longer fail. Four out-of-baseline identities were each rerun in isolation and did not reproduce.
- [x] `npm run typecheck` passes after installing the task lockfile dependencies and generating Prisma Client from the pinned Database submodule.
- [x] Targeted lint on changed Commerce files passes with 0 errors; two existing hook warnings remain in untouched `src/studio/code-response/code-response-panel.tsx`.
- [x] `npm run build` succeeds with pinned Node `v24.19.0` and task-local lockfile dependencies; package/smoke, Prisma generation and Next.js production build all pass.
- [x] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Commerce task.

## Implementation Notes

None

## Completion Report

### Status

Attempt 1 submitted for Architect review. The generic Studio page/detail router extraction is complete, public exports and specialised early returns remain in place, and all required build/typecheck/lint gates pass. The full suite remains non-green with baseline and isolated suite-load failures recorded below.

### Files Changed

- `components/studio-workspace.tsx`
- `components/studio-workspace/studio-page-content.tsx`
- `tests/studio-page-content.test.tsx`

### Work Completed

- Moved `PageContent`, `Detail` and the `Discovery` wrapper into `studio-page-content.tsx`, retaining the Explore schema guard/key, Release/Shop selection, dirty navigation guard, parent/back destinations, headings and `StudioState` handling.
- Reduced the public `StudioWorkspace` module to its public prop/type boundary, accepted controller wiring, Agent Configuration and ToolAuthoring early returns, and shared heading/unknown-operation/loading/list/detail composition.
- Added four focused tests for Explore schema/key-state forwarding, Release/Shop list selection, detail identity/back-navigation and Release detail selection.
- Left the controller, Release/Shop presentation modules, source-inspection tests, server actions and all frozen tests unchanged.

### Validation Results

- Frozen SHA-256 checks passed for `tests/studio-workspace.test.tsx`, `tests/agent-configuration-screen-state.test.tsx` and `tests/external-tools-ui.test.tsx`. The protected-file diff is empty; `git diff --check` passes.
- The new router test file passes 4/4. The required focused six-file run completed with 115 passed and 6 failed; all six failures are the exact frozen `tests/studio-workspace.test.tsx` identities listed by `ARCH025-COMMERCE-TEST-001`. Agent Configuration, External Tools UI and both accepted source-inspection suites pass.
- `npm run typecheck` passes with the task lockfile dependencies and Prisma Client generated for the exact Database submodule commit. The first typecheck used a stale `node_modules` symlink and produced inherited shared-package/Prisma errors plus two test fixture cast errors; the test fixture errors were fixed, and the final clean-dependency typecheck has no diagnostics.
- Targeted lint passes with zero errors. It reports two existing `react-hooks/exhaustive-deps` warnings in untouched `src/studio/code-response/code-response-panel.tsx`.
- `npm run build` passes with exit code 0 under Node `v24.19.0` using task-local dependencies: manuals package/smoke, code-runtime package/smoke, Prisma Client generation, Next.js production compilation, static page generation and route tracing all completed. An initial build using the shared dependency symlink (and Node `v24.21.0`) failed packaged helper smoke; the task lockfile was then installed locally, the pinned Node bootstrap selected `v24.19.0`, and the complete build passed. The clean local install was preserved under `/tmp/ARCH-025-COMMERCE-005-node_modules-clean-install`; the initial shared `node_modules` symlink was restored after validation.
- Full `npm test` completed with 23 failed files / 35 failed tests, 139 passed files / 1,355 passed tests, and 5 skipped files / 9 skipped tests. Thirty-one failed identities match the stable set in `ARCH025-COMMERCE-TEST-001`; two stable External Tools UI failures did not recur. The baseline's six collection failures did not recur. Four out-of-baseline identities were investigated: `tests/code-request-processor.test.ts` (1), `tests/code-runtime-proof.test.ts` (2), and the readiness abort case in `tests/readiness-docker.test.ts` (1). The first two files pass in isolation; readiness abort passes in isolation. The documented readiness timeout identity remains baseline-covered and failed during the isolated rerun. No out-of-baseline failure reproduced as a task regression.
- Full suite test identities that did not recur from the stable baseline are improvements; they were not recreated. No task-owned focused/frozen regression was found.

### Prepared Execution Packet

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-COMMERCE-005`, `task/ARCH-025-COMMERCE-005`; launcher start head `05444396304cd257e032fab57aaa1159bc7af82e`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-COMMERCE-005`, `task/ARCH-025-COMMERCE-005`; launcher start head `9f97998112428fcafe65a5c8344b3e7be2ff83a6`.
- Start synchronization for both task branches: task-branch fast-forward `not-needed`; `origin/main` `already-current`. Shared/default workspace and implementation checkouts were not switched or used for task implementation; no other task worktree was reused.
- Recursive submodules: `git submodule sync --recursive` and `git submodule update --init --recursive` passed; Database was initialized at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.
- Dependency gate: `ARCH-025-COMMERCE-004` complete and passed. Attempt 1 was claimed by `copilot` at `2026-10-03T10:58:42Z`; parent claim commit `4dd5c64720537696bef34c32ebfea95c1d5d25cf` was committed and pushed.
- Implementation commit `32b0fdd6a81af0adf260b54d3afed37ba2dff68e` was pushed to `origin/task/ARCH-025-COMMERCE-005`; its local and remote heads match.

### Deviations

The original linked `node_modules` resolved to stale shared-package and Prisma artifacts and the shell initially selected Node `v24.21.0`. To validate against the task's exact lockfile, dependencies were installed locally and the workspace bootstrap selected the pinned Node `v24.19.0`; after validation, the original symlink was restored and the clean installation preserved outside the repository. No product/runtime scope was changed.

### Assumptions

The six frozen StudioWorkspace failures remain covered by `ARCH025-COMMERCE-TEST-001`; the three out-of-baseline file identities were tested in isolation and did not reproduce, consistent with suite-load/runtime variance outside the task-owned modules.

### Unresolved Issues

- The repository-wide test command remains non-green under the documented baseline plus intermittent out-of-baseline failures described above. No task-introduced regression was identified; the failures are outside the authorized files and the novel identities passed in isolation.

### Architectural Concerns

None identified. The shell continues to delegate orchestration, Release/Shop behavior, and specialised Tool/Agent Configuration workflows to their accepted owners.

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
