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
status: in_progress
priority: 30
executor: copilot
claimed_at: 2026-09-24T17:39:05Z
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
