---
id: ARCH-021-COMMERCE-029
architecture_id: ARCH-021
title: Remove production Studio service function props
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-028
  - ARCH-021-COMMERCE-001
  - ARCH-021-COMMERCE-002
  - ARCH-021-COMMERCE-003
  - ARCH-021-COMMERCE-004
  - ARCH-021-COMMERCE-005
  - ARCH-021-COMMERCE-006
enables: []
created: 2026-09-24
updated: 2026-09-24
---

# Remove production Studio service function props

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`


## Objective

Make the normal Studio React boundary serializable: server pages load DTOs, client domain screens invoke named Server Actions, and production no longer passes `StudioServices`, Connection ports, External HTTP UI ports or other server-created function bundles into client components.

## Context

`ProductionStudioPage` currently constructs `StudioServices`, `ExternalHttpUiPort`, and Agent Configuration action objects and passes function-valued props into the client `StudioWorkspace`. This pattern has already produced Server/Client-boundary failures and obscures ordinary exceptions.

## Scope

Primary files:

```text
components/production-studio-page.tsx
components/studio-workspace.tsx
src/studio/server-services.ts
src/studio/server-actions.ts
src/studio/contracts.ts
src/studio/connections/server-actions.ts
src/studio/connections/* client components
src/studio/external-http/ports.ts
src/studio/external-http/editor.tsx
app/features/**
app/tools/**
app/explore/**
app/capabilities/**
app/releases/**
app/shops/**
app/connections/**
```

Only touch a route/domain when required to remove a production function prop. Do not redesign page visuals.

## Out of Scope

- Removing repository-local interfaces around real external boundaries.
- Removing test-only/in-memory adapters.
- Live Tool execution.
- Phase-3 Tool contract changes.
- Rewriting unrelated domain algorithms.

## Requirements

### R1. `ProductionStudioPage` serializable props only

After this task, `ProductionStudioPage` must not pass any prop whose runtime value is a server-created function bundle into a Client Component.

Specifically remove production props equivalent to:

```text
services={getStudioServices()}
externalHttpPort={...}
agentConfigurationActions={...}
agentConfigurationTemplateActions={...}
agentConfigurationPromptActions={...}
renderCodePanel={...}
```

`productionCodePanel` boolean may remain only if serializable and still required.

### R2. `StudioWorkspace` no longer accepts `StudioServices`

Remove `services: StudioServices` from client `StudioWorkspace` public props.

Initial page/detail DTOs are loaded by the relevant Server Component/page wrapper and passed serializably.

Client mutations/refreshes call named Server Actions directly.

### R3. Domain action files

Reuse existing `src/studio/server-actions.ts` and domain Server Action files. Split them into additional domain files only where necessary; do not introduce a generic client-to-server port registry.

### R4. Connections

Production Connections route clients must receive serializable initial data and call `src/studio/connections/server-actions.ts` directly.

Fixture `ConnectionPort` implementations may remain for component tests, but production route composition must not create/pass one.

### R5. External HTTP authoring

The external editor may retain a repository-local interface for pure client-local transformation/testing, but production server operations must be named Server Actions, not a server-created `ExternalHttpUiPort` object passed as a prop.

### R6. Error behavior

Named Server Actions must preserve typed domain errors. Client catch blocks must not map arbitrary thrown exceptions to success/empty/unknown without rendering/logging the actual failure class.

### R7. StudioWorkspace responsibility

`StudioWorkspace` remains shell/navigation/shared composition only. Do not move domain-specific state back into it while removing ports.

## Work Items

- [ ] Remove `StudioServices` production client prop.
- [ ] Convert initial reads to serializable Server Component DTOs.
- [ ] Convert client mutations/refreshes to named Server Actions.
- [ ] Remove production ConnectionPort prop composition.
- [ ] Remove production ExternalHttpUiPort server-created prop composition.
- [ ] Preserve test-only adapters where useful.
- [ ] Update focused route/component tests.

## Interfaces / Contracts

Normal internal UI boundary:

```text
Server Component -> serializable DTO -> Client Component -> named Server Action -> domain service
```

External boundaries may still use interfaces inside server code.

## Dependencies

- ARCH-021-COMMERCE-028
- ARCH-021-COMMERCE-001
- ARCH-021-COMMERCE-002
- ARCH-021-COMMERCE-003
- ARCH-021-COMMERCE-004
- ARCH-021-COMMERCE-005
- ARCH-021-COMMERCE-006

## Enables

None. `moda_architect` must re-review/redefine the paused Phase-3 frontier after this task and the private-MCP simplification tasks are complete.

## Acceptance Criteria

- [ ] No production `StudioServices` object crosses into a Client Component.
- [ ] No production server-created ConnectionPort crosses into a Client Component.
- [ ] No production server-created External HTTP port crosses into a Client Component.
- [ ] Normal UI errors remain visible and typed.
- [ ] Existing Studio routes retain functional behavior.
- [ ] Test adapters are not mistaken for production composition.

## Validation

- [ ] focused Studio route tests
- [ ] focused Connections tests
- [ ] focused Tool/External editor composition tests
- [ ] Next production build or repository-declared equivalent
- [ ] targeted ESLint/typecheck
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.


## Implementation Notes

Do not remove interfaces around Shopify, external HTTP transport, model providers or QuickJS. This task removes function-valued React production composition, not all dependency inversion.

## Completion Report

### Status

Ready for Review

### Files Changed

- `app/connections/[id]/page.tsx`
- `app/connections/page.tsx`
- `app/preview/page.tsx`
- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `components/unavailable-studio-workspace.tsx`
- `src/studio/connections/connections-route-client.tsx`
- `src/studio/connections/connections-ui.tsx`
- `src/studio/selected-shop.ts`
- `tests/agent-configuration-screen-state.test.tsx`
- `tests/browser-evidence/main.tsx`
- `tests/connections-route-composition.test.tsx`
- `tests/external-tools-ui.test.tsx`
- `tests/studio-workspace.test.tsx`

### Work Completed

- Removed production `StudioServices` function-bundle composition from `StudioWorkspace`; production pages now pass serializable initial page/detail DTOs and client mutations use named Studio Server Actions.
- Removed production ConnectionPort composition from Connections routes. Connection pages hydrate serializable initial list/detail data and use `src/studio/connections/server-actions.ts` for production reads and mutations; fixture ports remain available only through explicit test props.
- Removed production ExternalHttpUiPort construction from route composition. External HTTP authoring retains its local interface for client editor behavior and fixture tests, while production mutations use named Server Actions.
- Kept `renderCodePanel={composedCodePanel}` as internal client-to-client composition inside `StudioWorkspace`; no Server Component creates or passes it, so it does not cross the production server/client boundary and preserves the shell/editor responsibility in R1/R7.
- Updated focused route, Connections, agent-configuration, external-editor, browser-evidence and StudioWorkspace tests to use explicit fixture adapters and serializable production composition.

### Requirements Mapping

- R1/R2: `components/production-studio-page.tsx`, `components/studio-workspace.tsx`, `app/preview/page.tsx`, and the Studio route wrappers pass DTOs/serializable values only; the public `services` prop is removed.
- R3/R6/R7: existing named actions remain the production mutation/read path; StudioWorkspace remains shared shell/composition and preserves typed result handling.
- R4: `app/connections/page.tsx`, `app/connections/[id]/page.tsx`, `src/studio/connections/connections-route-client.tsx`, and `src/studio/connections/connections-ui.tsx` use serializable initial data and direct named connection actions; fixture ports are test-only.
- R5: `components/studio-workspace.tsx` and `src/studio/external-http/ports.ts` retain only the local editor/fixture interface path; production route composition no longer creates or passes a server-created external HTTP port.

### Validation Results

- Focused tests: `npm exec vitest run tests/connections-route-composition.test.tsx tests/connections-ui.test.tsx tests/external-tools-ui.test.tsx tests/studio-workspace.test.tsx tests/agent-configuration-screen-state.test.tsx` passed: 5 files, 59 tests.
- Production-boundary static check found no production `StudioWorkspace` service/port/action prop composition and no production `ConnectionsPage port` prop composition.
- `npm run lint` passed with 0 errors and 8 existing warnings in unrelated files/components.
- `git diff --check` passed.
- `npm run typecheck` is blocked by 15 pre-existing errors in `app/api/studio/code-response/validate/route.ts` and unrelated tests (`agent-configuration-effective`, `agent-configuration-prompts-postgres`, `c20-integration-fixture`, `connections-production`, `external-wiring`, `local-external-mcp-diagnostic`). None are in the changed 14-file implementation set.
- `npm run build` is blocked by the same pre-existing missing preview modules referenced by `app/api/studio/code-response/validate/route.ts`: `lib/preview/http`, `lib/preview/runtime`, and `src/commerce/preview/types`.

### Deviations

- `renderCodePanel` remains a client-to-client prop used internally by `StudioWorkspace`; it is not server-created or passed by `ProductionStudioPage`, and removing it would violate the intended shared editor composition without improving R1/R7 conformance.
- Repository-wide typecheck and production build could not pass because of the documented existing preview-module/type errors outside this task's changed files. Focused behavior and lint validation passed.

### Assumptions

- The canonical implementation worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-029` and the canonical parent worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-029`.
- The implementation repository's committed/pushed branch is `task/ARCH-021-COMMERCE-029` at `2adb933742d884b6434277d2263f75da46f06d0a`.

### Unresolved Issues

- Repository baseline preview-module failures remain for architect/developer follow-up; no task-owned repair was made because the missing modules and unrelated type errors are outside this bounded task.

### Architectural Concerns

- None identified. The parent worktree's `moda-interact-commerce` gitlink remains at recorded commit `01c550c3e3f55dd23a4ecc9514c846bb88cf2067`; the implementation branch is intentionally published separately and the parent gitlink was not changed.

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
