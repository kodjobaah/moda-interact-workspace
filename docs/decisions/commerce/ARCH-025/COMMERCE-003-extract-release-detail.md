---
id: ARCH-025-COMMERCE-003
architecture_id: ARCH-025
title: Extract Release Detail clone activation and rollback view
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
  - ARCH-025-COMMERCE-002
enables:
  - ARCH-025-COMMERCE-004
created: 2026-10-02
updated: 2026-10-02
---

# Extract Release Detail clone activation and rollback view

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract Release Detail clone-as-new, activation and rollback presentation into a dedicated module while preserving Studio composer handoff, role gating and active-pointer fencing.

## Context

After COMMERCE-002, Release Detail remains a separate workflow with different state/failure semantics from composition: clone handoff, privileged activation/rollback confirmation and active-pointer CAS fencing.

## Scope

Authorised implementation surface:

```text
components/studio-workspace.tsx
components/studio-workspace/release-detail.tsx
tests/release-detail.test.tsx
```

## Out of Scope

Controller or Release Composer redesign, release server-action changes, response-contract schema changes, Shop/page routing extraction.

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

### R1 — Release Detail ownership

Move the complete current `ReleaseDetail` presentation/workflow into `components/studio-workspace/release-detail.tsx`. Local confirmation/reason state remains local.

### R2 — edit-as-new handoff

Preserve `composer.setRelease(...)` exactly: a newly generated Studio operation/handoff ID using the accepted COMMERCE-001 helper, exact members, `structuredClone(responseContract)`, existing validation hash, blank reason and return route `/releases/<id>?tab=response-contract`; then navigate to `/releases?cloneResponseFrom=<id>`.

### R3 — activation/rollback role and fence

Preserve SUPER_ADMIN gating, ADMIN explanatory copy, previous-release rollback label, confirmation dialog, non-empty reason requirement, current active-pointer version fence, exact activate/rollback server-action payloads and current success/reload behaviour through `runCommand`.

### R4 — current dirty/cancel quirk

Typing the confirmation reason continues to mark global dirty. Cancelling the dialog currently only closes confirmation and does not clear global dirty; preserve that behaviour during extraction rather than silently normalising it.


## Work Items

- [ ] Move Release Detail into the dedicated module.
- [ ] Reuse the accepted internal operation-ID helper and workspace command/navigation contract.
- [ ] Add focused clone/role/fence/dirty-confirmation tests.
- [ ] Keep COMMERCE-001 controller and COMMERCE-002 Release Composer unchanged.


## Interfaces / Contracts

Consumes accepted COMMERCE-001 common props plus `useStudioComposer`; no new public contract.

## Dependencies

- `ARCH-025-COMMERCE-002`

## Enables

- `ARCH-025-COMMERCE-004`

## Acceptance Criteria

- [ ] Edit-as-new handoff shape and destinations are unchanged.
- [ ] Activation/rollback role gating, confirmation and active-pointer fencing are unchanged.
- [ ] Current dirty-on-reason / cancel-does-not-clear-dirty behaviour is preserved.
- [ ] Frozen 13/3/90-test assets remain unchanged and pass.


## Validation

- [ ] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/studio-workspace.test.tsx':'400ce6b68cb5a9fdeecf9233bc2b3f58a42742c974da2c5b6ffd2b5a16ae44a7','tests/agent-configuration-screen-state.test.tsx':'72c71a09eaf5bdc2d79c686cf5ec43d5abfd49cfe421cadedbbe665140582b0a','tests/external-tools-ui.test.tsx':'97ffbc70e29d4ff60a48e5aabd0ff3faec6dea7984ed0f239fcb4a8fc868f4d3'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected frozen hashes.
- [ ] `npx vitest run tests/release-detail.test.tsx tests/studio-workspace.test.tsx` passes.
- [ ] `git diff -- components/studio-workspace/use-studio-workspace-controller.ts components/studio-workspace/release-composer.tsx tests/legacy-capability-surface.test.ts tests/arch024-preview-cleanup.test.ts` is empty.

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
