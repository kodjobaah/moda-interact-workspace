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
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 2
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

Changes Requested

### Review Notes

Attempt 2 resolves the substantive Attempt 1 defects:

- `StudioWorkspace` no longer accepts `StudioServices` / `fixtureAdapter` in its production React props;
- Studio tests now drive the same named `src/studio/server-actions` boundary through module mocks rather than passing a `StudioServices` object into the production component;
- unexpected task-owned server exceptions are logged through `@modainteract/moda-interact-shared/logging` with the raw `Error`;
- task-owned client catches now preserve a bounded thrown failure class rather than silently collapsing arbitrary rejection into an indistinguishable domain result;
- empty reconciliation catches were removed;
- Agent Configuration and selected-shop production composition regressions now model the named-Server-Action + serializable-DTO architecture;
- the submitted expanded focused packet passes 8 files / 69 tests;
- the reported typecheck/build blockers remain the already-recorded unrelated Commerce preview/integration diagnostics and no Attempt 2-owned diagnostic is reported.

No further logging/reconciliation redesign is requested.

However, after applying the architecture principle agreed with the developer during review — **tests must exercise the same production composition rather than adding production APIs solely for test injection** — three remaining production seams must be removed before this task can be accepted.

The distinction is important:

- **Allowed:** helpers, in-memory fixtures, wrappers and state that exist only under `tests/` (or an explicitly test-support module) and are used to configure mocks.
- **Not allowed:** a prop, branch or exported runtime alias in a production component/module whose only reason to exist is to let tests inject a different execution path.

The goal is one production execution model and tests that replace its real module boundaries.

#### Finding 1 — `StudioWorkspace.externalHttpPort` is a test-only production prop

`components/studio-workspace.tsx` still publicly accepts:

```ts
externalHttpPort?: ExternalHttpUiPort;
```

Production `ProductionStudioPage` never passes this prop. Production instead passes the serializable:

```ts
externalHttpCatalogue
```

and `StudioWorkspace` correctly creates the client-local `ExternalHttpUiPort` from that catalogue.

The only callers passing `externalHttpPort` are tests in `tests/external-tools-ui.test.tsx`.

That leaves an alternate function-valued React composition path solely for tests and keeps open the same class of accidental Server -> Client misuse this task exists to eliminate.

Attempt 3 must:

1. remove `externalHttpPort` from the exported `StudioWorkspace` prop contract;
2. construct the client-local port only from serializable `externalHttpCatalogue` in production code;
3. update external-tool component tests to provide the same serializable catalogue path production uses;
4. where a pure adapter needs direct unit coverage, call `createExternalHttpSamplePort(catalogue)` directly outside React rather than injecting its returned function object through `StudioWorkspace`.

The internal client-to-client `ExternalHttpUiPort` used by `ToolDetail` / `ExternalHttpEditor` may remain because it is a genuine production client abstraction created on the client from serializable state. The prohibited seam is the **public `StudioWorkspace` injection prop**.

#### Finding 2 — `StudioWorkspace.renderCodePanel` is a dead/test-style function prop

`components/studio-workspace.tsx` also publicly accepts:

```ts
renderCodePanel?: (props: ExternalCodePanelSlotProps) => React.ReactNode;
```

No production caller supplies it, and the submitted test packet does not require an external caller either. The production JavaScript response panel is already composed internally through the serializable `productionCodePanel` flag plus the client-created External HTTP adapter.

Attempt 3 must remove `renderCodePanel` from the exported `StudioWorkspace` prop contract and remove the dead fallback path:

```ts
... : renderCodePanel
```

Do not replace it with another test-only wrapper/context/registry in production code.

The internal `ExternalHttpEditor.renderCodePanel` client-to-client slot may remain if it is genuinely used by production `ToolDetail`; that is not an RSC boundary and is not test-only.

#### Finding 3 — `ConnectionsPage.port` is a test-only alternate execution architecture

`src/studio/connections/connections-ui.tsx` still exports:

```ts
ConnectionsPage({ port, ... }: { port?: ConnectionPort; ... })
```

and threads that optional `ConnectionPort` through `ConnectionDetail` and `CredentialPanel`.

Production `ConnectionsRouteClient` never supplies `port`; it always uses the named functions from:

```text
src/studio/connections/server-actions.ts
```

Only `tests/connections-ui.test.tsx` supplies `port`.

This means production and tests still have two distinct client execution paths:

```text
production -> named Server Actions
tests      -> injected ConnectionPort
```

Attempt 3 must reduce this to one path:

```text
production -> named Server Actions
tests      -> mock the same named Server Action module
```

Specifically:

1. remove `port?: ConnectionPort` from `ConnectionsPage`;
2. remove the `port` prop from `ConnectionDetail` and `CredentialPanel`;
3. remove client branches of the form:

   ```ts
   port ? port.someOperation(...) : namedServerAction(...)
   ```

   and invoke the named Server Action directly;
4. keep `ConnectionPort` as a server-side/domain adapter where it is genuinely useful (`production.ts`, server actions, pure fixture/unit tests);
5. update `tests/connections-ui.test.tsx` so its mocked `src/studio/connections/server-actions` functions delegate to a test-owned `createConnectionFixtures()` instance or equivalent fixture state;
6. do not add `NODE_ENV === "test"`, global runtime registries, test-only React context, or another production injection prop.

A local helper inside `tests/connections-ui.test.tsx` that installs a fixture behind mocked named actions is acceptable because it is test code, not a production API.

#### Finding 4 — remove production exports that exist only as fixture aliases

`src/studio/external-http/ports.ts` currently exports:

```ts
createExternalHttpFixturePort()
createExternalHttpCataloguePort()
```

Neither is used by production runtime code. Production uses:

```ts
createExternalHttpSamplePort(catalogue)
```

Attempt 3 must remove those two test-only aliases from the production module.

Tests must:

- create test-owned serializable `ExternalHttpCatalogue` DTOs;
- use `externalHttpCatalogue` when rendering `StudioWorkspace`;
- call the real production `createExternalHttpSamplePort(catalogue)` directly for pure adapter tests.

The synthetic sample-processing behavior inside `createExternalHttpSamplePort` remains production authoring behavior for this phase and is **not** to be removed.

Do not broaden this correction into deleting every existing fixture/in-memory helper in the repository. Test fixture implementations are allowed; they simply must not force alternate production React/runtime APIs.

### Required production-surface invariant

After Attempt 3 the following must be true:

```text
ProductionStudioPage
    -> serializable StudioWorkspace props only
    -> named Server Actions for server interaction

ConnectionsRouteClient
    -> serializable ConnectionsPage props only
    -> named Connections Server Actions

tests
    -> same production components
    -> same named-action imports, replaced by module mocks where deterministic fixtures are needed
```

Production React public props must not contain a function/port/service value solely to support tests.

### Deterministic source audit

Before returning the task, run:

```bash
rg -n \
  "fixtureAdapter|externalHttpPort\\?:|renderCodePanel\\?:|port\\?: ConnectionPort" \
  components/studio-workspace.tsx \
  src/studio/connections/connections-ui.tsx
```

Expected result:

```text
no matches
```

Also run:

```bash
rg -n \
  "createExternalHttpFixturePort|createExternalHttpCataloguePort" \
  src
```

Expected result:

```text
no matches
```

The internal production uses of `ExternalHttpUiPort`, `ConnectionPort`, and `ExternalHttpEditor.renderCodePanel` are not forbidden when they are genuine runtime abstractions and are not exposed as test-only React injection seams.

### Test requirements

Update the focused tests so they exercise the single production composition.

At minimum the focused packet must include:

```text
tests/agent-configuration-production.test.tsx
tests/connections-production.test.ts
tests/connections-route-composition.test.tsx
tests/connections-ui.test.tsx
tests/external-tools-production.test.ts
tests/external-tools-ui.test.tsx
tests/selected-shop-route.test.tsx
tests/studio-workspace.test.tsx
tests/studio-services-errors.test.ts
```

Requirements for that packet:

- `StudioWorkspace` tests configure `InMemoryStudioServices` only behind mocked named Studio Server Actions.
- External-tool React tests do not pass `externalHttpPort`; they pass a serializable catalogue.
- Connections React tests do not pass `ConnectionPort`; they configure mocked named Connections Server Actions.
- Production composition regressions continue proving server pages/routes do not forward function-valued service/port props.
- Existing unexpected-failure-class and shared-logger regressions continue to pass.
- No test uses a production-only `NODE_ENV === "test"` branch.

### Task-state/report reconciliation

The implementing agent owns the task checklists. Attempt 2 returned with every Work Item, Acceptance Criterion and Validation item still unchecked even though the Completion Report says most are satisfied.

Attempt 3 must reconcile those checkboxes honestly:

- mark an item `[x]` only when the final Attempt 3 implementation and required validation proves it;
- leave required typecheck/build items unchecked only if the repository baseline genuinely prevents them, and record the exact unchanged baseline diagnostics;
- do not return to review with the entire checklist unchecked.

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

Submitted Attempt 2 evidence:

```text
focused expanded tests: 8 files / 69 tests passed
pnpm lint: PASS (0 errors; unrelated existing warnings)
git diff --check: PASS
```

The reported repository typecheck/build blockers are the documented missing preview modules / unrelated baseline test diagnostics, with no Attempt 2-owned diagnostics reported.

The review archive does not contain `node_modules`, so the architect could not independently rerun Vitest/ESLint/build from this archive.

### Architecture Conformance

Partial.

The original Server Component -> Client Component serialization defect is fixed and the error/logging correction is conformant. The remaining non-conformance is narrower: some production Client Component APIs still contain alternate function-valued execution seams solely for tests.

This review adopts the developer-confirmed testing invariant:

> Test-only helpers are normal; test-only **production APIs** are not. Tests should replace the same module boundaries production uses rather than adding an alternate runtime composition to production components.

### Follow-up

Reclaim this same task as Attempt 3.

Implement only the test/runtime-boundary corrections above. Preserve the accepted Attempt 2 logging, error behavior, serializable server composition and domain behavior.

Do not:

- redesign Studio visuals;
- change Tool/Connection business semantics;
- remove genuine server-side/domain interfaces;
- remove genuine production client-local External HTTP abstractions;
- create a generic port registry;
- create a production test context/provider;
- add `NODE_ENV === "test"` runtime behavior;
- repair unrelated preview/typecheck/build baseline debt.

After implementation:

1. run the required focused packet;
2. run targeted ESLint for every changed file;
3. run repository typecheck/build as required by the task and classify only the already-documented unrelated baseline diagnostics;
4. run the deterministic source audits above;
5. run `git diff --check`;
6. reconcile Work Items / Acceptance Criteria / Validation checkboxes;
7. record Attempt 3 launcher-prepared parent/implementation worktrees, start synchronization/base evidence, recursive database-submodule evidence, implementation commit, parent report commit and final clean/upstream branch state;
8. set:

   ```yaml
   status: review
   executor: null
   claimed_at: null
   attempt: 3
   ```

9. return to `moda_architect` and STOP.

`ARCH-021-SYSTEM-TEST-001` remains Pending until COMMERCE-029 is architect-accepted Complete.
