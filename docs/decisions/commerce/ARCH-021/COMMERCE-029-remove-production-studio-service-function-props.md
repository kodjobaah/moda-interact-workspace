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
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 3
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

- [x] Remove `StudioServices` production client prop.
- [x] Convert initial reads to serializable Server Component DTOs.
- [x] Convert client mutations/refreshes to named Server Actions.
- [x] Remove production ConnectionPort prop composition.
- [x] Remove production ExternalHttpUiPort server-created prop composition.
- [x] Preserve test-only adapters where useful.
- [x] Update focused route/component tests.

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

- [x] No production `StudioServices` object crosses into a Client Component.
- [x] No production server-created ConnectionPort crosses into a Client Component.
- [x] No production server-created External HTTP port crosses into a Client Component.
- [x] Normal UI errors remain visible and typed.
- [x] Existing Studio routes retain functional behavior.
- [x] Test adapters are not mistaken for production composition.

## Validation

- [x] focused Studio route tests
- [x] focused Connections tests
- [x] focused Tool/External editor composition tests
- [ ] Next production build or repository-declared equivalent: blocked by the unchanged missing preview modules `lib/preview/http`, `lib/preview/runtime`, and `src/commerce/preview/types`.
- [ ] targeted ESLint/typecheck: lint passed; typecheck remains blocked by those three missing preview modules and the six unchanged baseline test diagnostic groups recorded below.
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.


## Implementation Notes

Do not remove interfaces around Shopify, external HTTP transport, model providers or QuickJS. This task removes function-valued React production composition, not all dependency inversion.

## Completion Report

### Status

Ready for Review

### Attempt 3 Files Changed

- `components/studio-workspace.tsx`
- `src/studio/connections/connections-ui.tsx`
- `src/studio/external-http/ports.ts`
- `tests/connections-route-composition.test.tsx`
- `tests/connections-ui.test.tsx`
- `tests/external-tools-production.test.ts`
- `tests/external-tools-ui.test.tsx`

### Attempt 3 Correction Mapping

- R1/R2: the exported `StudioWorkspace` boundary remains serializable; the external HTTP client-local port is constructed only from `externalHttpCatalogue`, and no `externalHttpPort` or `renderCodePanel` public props remain.
- R4: `ConnectionsPage`, `ConnectionDetail` and `CredentialPanel` use named connection Server Actions directly; no `ConnectionPort` prop or conditional port branch remains. Connection UI tests mock the named action module and delegate to test-owned fixture state.
- R5: removed production `createExternalHttpFixturePort` and `createExternalHttpCataloguePort` exports; pure adapter coverage calls `createExternalHttpSamplePort(catalogue)` directly.
- R6/R7: existing typed error rendering and client-only external editor composition remain unchanged.

### Attempt 3 Validation Results

- Focused packet passed: `pnpm exec vitest run tests/agent-configuration-production.test.tsx tests/connections-production.test.ts tests/connections-route-composition.test.tsx tests/connections-ui.test.tsx tests/external-tools-production.test.ts tests/external-tools-ui.test.tsx tests/selected-shop-route.test.tsx tests/studio-workspace.test.tsx tests/studio-services-errors.test.ts` — 9 files, 71 tests.
- Required audits passed with no matches: `fixtureAdapter|externalHttpPort?:|renderCodePanel?:|port?: ConnectionPort` in the specified production files, and `createExternalHttpFixturePort|createExternalHttpCataloguePort` under `src`.
- `pnpm lint` passed with 0 errors and 8 pre-existing warnings in unrelated files.
- `pnpm typecheck` remains baseline-blocked with 15 diagnostics: three missing preview modules plus unchanged diagnostics in `agent-configuration-effective`, `agent-configuration-prompts-postgres`, `c20-integration-fixture`, `external-wiring`, `local-external-mcp-diagnostic`, and `selected-shop-context`; no Attempt 3-owned file is listed.
- `pnpm build` reached runtime packaging, packaged-runtime smoke, Prisma generation and Next compilation, then failed on the same three missing preview modules: `lib/preview/http`, `lib/preview/runtime`, and `src/commerce/preview/types`.
- `git diff --check` passed. Database submodule remained `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.

### Attempt 3 Publication Evidence

- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-029`
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-029`
- Mirrored branches: `task/ARCH-021-COMMERCE-029`
- Implementation commit pushed: `4ab1cf1` (`fix(commerce): remove remaining studio test seams`)
- Parent claim commit: `4c17ad6a0646bd147b5aa87330aa8e701e920ba4`
- Architect Review was not modified.

### Attempt 2 Files Changed

- `components/studio-workspace.tsx`
- `src/commerce/integration/studio/services.ts`
- `src/studio/connections/connections-ui.tsx`
- `src/studio/connections/production.ts`
- `src/studio/external-http/ports.ts`
- `src/studio/selected-shop.ts`
- `tests/agent-configuration-production.test.tsx`
- `tests/connections-production.test.ts`
- `tests/connections-ui.test.tsx`
- `tests/external-tools-production.test.ts`
- `tests/external-tools-ui.test.tsx`
- `tests/selected-shop-route.test.tsx`
- `tests/studio-workspace.test.tsx`
- `tests/studio-services-errors.test.ts`

### Correction Mapping

- R2: removed the `fixtureAdapter`/`StudioServices` prop and module-global fixture injection from `StudioWorkspace`; production props are serializable and fixture behavior remains test-local.
- R6: unexpected server translation paths now emit raw `Error` objects through the shared logger using approved event names, while preserving bounded client-visible failure classes for reconciliation, read, credential and connection-action failures without secrets.
- R4/R5: updated production-boundary adapters and client handling so named Server Actions remain the production path; stale tests now model the current serializable route contracts and `getConnection` detail read.
- R1/R3/R7: retained named Server Actions and client-only composition without introducing a generic service/port registry; `renderCodePanel` remains internal client-to-client composition.

### Validation Results

- Focused expanded tests: `pnpm exec vitest run tests/agent-configuration-production.test.tsx tests/connections-production.test.ts tests/connections-ui.test.tsx tests/external-tools-production.test.ts tests/external-tools-ui.test.tsx tests/selected-shop-route.test.tsx tests/studio-workspace.test.tsx tests/studio-services-errors.test.ts` passed: 8 files, 69 tests.
- `pnpm lint` passed with 0 errors and 8 existing warnings in unrelated files.
- `pnpm typecheck` exited 2 with 15 existing diagnostics; no diagnostics remained in the Attempt 2-owned files. The blockers are the three missing preview modules in `app/api/studio/code-response/validate/route.ts` plus unrelated baseline tests (`agent-configuration-effective`, `agent-configuration-prompts-postgres`, `c20-integration-fixture`, `external-wiring`, `local-external-mcp-diagnostic`, and `selected-shop-context`).
- `pnpm build` reached runtime packaging, packaged-runtime smoke, Prisma generation, and Next compilation, then exited 1 on the same three missing preview modules: `lib/preview/http`, `lib/preview/runtime`, and `src/commerce/preview/types`.
- `git diff --check` passed.
- Database submodule remained `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.

### Publication Evidence

- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-029`
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-029`
- Implementation branch: `task/ARCH-021-COMMERCE-029`
- Implementation commit pushed: `4e62189` (`4e621896b31b0cf86cd5d915c1d26b6e0c2a24be`)
- Parent claim evidence: `6d281647bb72179d0e77fa69652b598bc3066ccf`
- The parent `moda-interact-commerce` gitlink was not changed.

### Unresolved Issues

- Repository-wide preview-module/typecheck blockers remain for architect/developer follow-up; no out-of-scope repair was made.

### Architectural Concerns

- None identified. Attempt 2 is ready for Architect Review.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 3 satisfies the remaining production/test-boundary corrections from Attempt 2.

The final production composition now has one execution model:

```text
ProductionStudioPage
    -> serializable StudioWorkspace props
    -> named Studio Server Actions

ConnectionsRouteClient
    -> serializable ConnectionsPage props
    -> named Connections Server Actions
```

The architect specifically verified the developer-confirmed testing invariant:

> Test helpers and fixture state may exist inside test code, but production React/component APIs must not expose alternate function-valued ports, service bundles or render callbacks solely for tests.

That invariant is now satisfied.

Production code no longer exposes:

```text
StudioWorkspace.fixtureAdapter
StudioWorkspace.externalHttpPort
StudioWorkspace.renderCodePanel
ConnectionsPage.port
ConnectionDetail.port
CredentialPanel.port
createExternalHttpFixturePort
createExternalHttpCataloguePort
```

The remaining `fixtureAdapter` / `port` names are confined to test-local wrappers/state that configure mocks for the same named Server Action modules production uses. They are not part of the production component API or runtime composition.

Accepted behavior:

- `StudioWorkspace` receives serializable page/detail/catalogue/configuration DTOs from server composition;
- client mutations and refreshes use named Server Actions;
- the External HTTP client-local adapter is created from serializable `externalHttpCatalogue`;
- Connections UI uses named Connections Server Actions directly;
- test fixture state delegates through mocked named Server Action modules rather than an alternate production port prop;
- genuine production client-local/server-side interfaces remain where they represent real runtime boundaries;
- Attempt 2 structured logging and bounded client-visible failure-class behavior remain intact;
- no `NODE_ENV === "test"` production branch, generic port registry, or production test context/provider was introduced.

The required source audits pass with no production matches:

```text
fixtureAdapter|externalHttpPort?:|renderCodePanel?:|port?: ConnectionPort
createExternalHttpFixturePort|createExternalHttpCataloguePort
```

The focused validation packet passed 9 files / 71 tests.

The repository-wide typecheck/build remain blocked only by the previously documented Commerce baseline. Architect inspection of `tsconfig.tsbuildinfo` confirms the current semantic diagnostics are limited to:

```text
app/api/studio/code-response/validate/route.ts
tests/agent-configuration-effective.test.ts
tests/agent-configuration-prompts-postgres.test.ts
tests/c20-integration-fixture.test.ts
tests/external-wiring.test.ts
tests/local-external-mcp-diagnostic.test.ts
tests/selected-shop-context.test.ts
```

None is an Attempt 3-owned changed file.

### Reviewed Files

- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `components/unavailable-studio-workspace.tsx`
- `src/commerce/integration/studio/services.ts`
- `src/studio/server-actions.ts`
- `src/studio/connections/connections-route-client.tsx`
- `src/studio/connections/connections-ui.tsx`
- `src/studio/connections/server-actions.ts`
- `src/studio/connections/production.ts`
- `src/studio/connections/fixtures.ts`
- `src/studio/external-http/ports.ts`
- `src/studio/external-http/editor.tsx`
- `tests/agent-configuration-production.test.tsx`
- `tests/connections-production.test.ts`
- `tests/connections-route-composition.test.tsx`
- `tests/connections-ui.test.tsx`
- `tests/external-tools-production.test.ts`
- `tests/external-tools-ui.test.tsx`
- `tests/selected-shop-route.test.tsx`
- `tests/studio-workspace.test.tsx`
- `tests/studio-services-errors.test.ts`
- task Completion Report
- parent ARCH-021 checkpoint state

### Validation Reviewed

Submitted Attempt 3 evidence:

```text
Focused packet: 9 files / 71 tests passed
Targeted lint: PASS
Required source audits: PASS
git diff --check: PASS
Database submodule: required commit synchronized
```

Architect independently inspected the submitted `tsconfig.tsbuildinfo` and confirmed no Attempt 3-owned file appears in the current semantic-diagnostic set.

The review archive does not contain `node_modules`, so the architect did not rerun Vitest/ESLint/Next build from the archive.

Implementation reviewed:

```text
4ab1cf14
```

Submitted parent report:

```text
825217af
```

### Architecture Conformance

Conforms.

The original Server Component -> Client Component serialization defect is eliminated without replacing it with test-only production APIs. Production and tests now share the same component/action architecture; tests substitute module boundaries only inside test code.

The task's intentionally blocked repository-wide build/typecheck items remain attributable to documented unrelated baseline diagnostics and do not represent a COMMERCE-029 regression.

### Follow-up

`ARCH-021-COMMERCE-029` is Complete.

All dependencies of `ARCH-021-SYSTEM-TEST-001` are now Complete, so the terminal simplification checkpoint system-test task becomes Ready.

Per the architecture lifecycle, the developer may leave `ARCH-021-SYSTEM-TEST-001` Ready while manually validating the completed checkpoint. Do not resume the paused Phase-3 task frontier merely because COMMERCE-029 is Complete; Phase-3 reconciliation follows terminal checkpoint validation.
