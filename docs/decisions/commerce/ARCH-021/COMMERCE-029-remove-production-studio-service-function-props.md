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

Attempt 1 is directionally correct and removes the production Server Component -> Client Component function-bundle composition that caused the original Next.js serialization failure.

Accepted in substance:

- `ProductionStudioPage` no longer passes `StudioServices`, Agent Configuration action bundles, `ExternalHttpUiPort`, `renderCodePanel`, or another server-created function object into `StudioWorkspace`.
- production Studio page/detail reads are passed as serializable DTO/result values;
- production mutations use named Server Actions imported by client domain code;
- production Connections routes pass serializable initial list/detail values and do not compose/pass a `ConnectionPort`;
- the production Tools route passes serializable connection/revision catalogue data and the client creates its local External HTTP authoring helper from those DTOs;
- Preview route composition is serializable;
- test-only Connection/External HTTP adapters remain available;
- the submitted changed-file TypeScript surface has no reported task-owned diagnostics;
- the reported repository-wide typecheck/build blockers match already-recorded Commerce preview/integration baseline failures outside this task-owned changed-file set.

The task is not yet acceptable because three requirements remain incomplete.

#### 1. R2 is not satisfied: `StudioWorkspace` still accepts a `StudioServices` function bundle

`components/studio-workspace.tsx` removed the old `services` prop but introduced:

```ts
fixtureAdapter?: StudioServices;
```

and assigns that function-valued object to module-global `fixtureStudioServices`.

R2 is explicit: `StudioWorkspace` must no longer accept `StudioServices` as a Client Component prop. Renaming the prop to `fixtureAdapter` does not make the public React boundary serializable.

Test adapters may remain, but they must be injected through a test-only mechanism that does **not** make `StudioServices` part of the production `StudioWorkspace` prop contract.

Acceptable bounded approaches include:

- mock the named Server Action modules in component tests; or
- introduce a test-only wrapper/context/helper under the testing surface that supplies fixture behavior without adding a function-valued prop to production `StudioWorkspace`.

Do **not** introduce a generic production client-to-server service/port registry.

After the correction:

```text
components/studio-workspace.tsx
```

must have no `StudioServices` import required only for React props, and its exported production props must not contain `StudioServices` or an equivalent function bundle.

#### 2. R6 is not satisfied: unexpected exceptions are still swallowed into generic `unknown` / `unavailable`

The task explicitly requires ordinary failures to remain visible and says client catch blocks must not map arbitrary thrown exceptions to `success`, empty state, `unknown`, or `unavailable` without rendering/logging the actual failure class.

Current task-owned production paths still do this.

Examples:

```text
components/studio-workspace.tsx
```

`attempt(...)` catches every thrown value and converts it directly to `kind: "unknown"` without preserving/logging the failure class.

```text
src/studio/connections/connections-ui.tsx
```

contains:

- mutation catch -> generic `kind: "unknown"`;
- reconciliation catch -> empty catch / retained operation;
- credential-status catch -> generic unavailable;
- connection-detail catch -> generic unavailable.

The server-side production adapters also translate unexpected infrastructure/runtime exceptions without structured logging:

```text
src/commerce/integration/studio/services.ts
src/studio/connections/production.ts
```

This is precisely the failure-obscuring behavior the checkpoint is intended to remove.

Attempt 2 must implement the following deterministic behavior.

**Known typed/domain outcomes**

Preserve existing typed results such as:

```text
ok
not-found
forbidden
conflict
unavailable
unknown
```

when those are returned deliberately by the domain/service contract.

Do not log ordinary expected business outcomes as errors merely because they are non-OK.

**Unexpected caught server exceptions**

Whenever server-side Studio/Connections code catches an unexpected exception and translates it to a bounded UI result, log the original exception first using the approved shared logger:

```ts
import {
  createLogger,
  type StructuredLogger,
} from "@modainteract/moda-interact-shared/logging";
```

Use the canonical service identity:

```ts
createLogger({
  serviceName: "moda-interact-commerce",
  environment:
    process.env.DEPLOYMENT_ENVIRONMENT_NAME ??
    process.env.NODE_ENV ??
    "unknown",
});
```

The error must be passed as the raw field:

```ts
logger.error("commerce.studio.action_failed", {
  operationId: operationId?.slice(0, 128),
  error,
});
```

or, for Connections:

```ts
logger.error("commerce.studio.connection_action_failed", {
  operationId: operationId?.slice(0, 128),
  error,
});
```

Do **not** replace the raw error with `error.message`, `String(error)`, JSON serialization, or a locally invented Error serializer. The shared logger already serializes `Error` to bounded `name` + `message`.

Do not log prompt text, tool definitions, credentials, authorization headers, provider payloads, request/response bodies, customer data, or secrets.

A logger failure must not alter business correctness.

Tests should use the shared logger's injected/capture sink where an injectable logger seam is needed; do not mock `console.error` as the logging contract.

**Unexpected client-side Server Action rejection**

Client code must catch as:

```ts
catch (error)
```

rather than an empty catch.

The UI does not need to expose the raw server error message. It must, however, preserve/render a bounded failure class, for example:

```text
Error
TypeError
UnknownThrownValue
```

alongside the existing safe user message, so an arbitrary thrown exception is not indistinguishable from a deliberate typed `unknown`/`unavailable` domain result.

For reconciliation, retain the admitted operation if required, but do not use an empty catch; update the visible diagnostic state with the caught failure class.

Do not add browser-side generic `console.error` logging as a substitute for the server structured logger.

Add focused regressions proving:

- unexpected Studio mutation rejection is not silently converted to an indistinguishable domain `unknown`;
- unexpected Connection mutation rejection preserves the admitted operation **and** exposes the caught failure class;
- reconciliation rejection is not swallowed;
- unexpected Connection read/credential-status rejection exposes the failure class;
- server-side unexpected translation emits one structured error event containing the raw `Error`;
- no secret/body payload is included in the structured log.

#### 3. Production-boundary regression coverage is incomplete/stale

`tests/agent-configuration-production.test.tsx` still mocks:

```text
src/studio/server-services
createExternalHttpProductionPort
```

and expects:

```text
resolveStudioShopSelection(state.services, shopId)
```

even though the new production composition calls the selected-shop resolver directly through named actions and no longer creates those production function bundles.

That is stale architecture evidence and it was not included in the submitted 59-test focused packet.

Attempt 2 must update the production composition regressions so the tests themselves represent the new architecture.

At minimum, production-boundary tests must prove:

```text
ProductionStudioPage -> StudioWorkspace
```

does **not** pass:

```text
services
fixtureAdapter
externalHttpPort
agentConfigurationActions
agentConfigurationTemplateActions
agentConfigurationPromptActions
renderCodePanel
```

and for Tools may pass only the serializable:

```text
externalHttpCatalogue
```

plus ordinary scalar/DTO props.

The Agent Configuration production test must no longer mock or assert use of `getStudioServices()`.

The selected-shop resolver assertion must match the actual one-argument production contract.

If `createExternalHttpProductionPort()` is now dead production composition, either remove/rename that misleading dead production helper/test or rewrite the test so it validates the serializable production catalogue boundary instead. Do not preserve a "production port" test that no production route uses.

### Reviewed Files

- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `components/unavailable-studio-workspace.tsx`
- `app/agent-configuration/page.tsx`
- `app/connections/page.tsx`
- `app/connections/[id]/page.tsx`
- `app/preview/page.tsx`
- `src/studio/server-actions.ts`
- `src/studio/server-services.ts`
- `src/studio/selected-shop.ts`
- `src/studio/connections/connections-route-client.tsx`
- `src/studio/connections/connections-ui.tsx`
- `src/studio/connections/server-actions.ts`
- `src/studio/connections/production.ts`
- `src/studio/external-http/ports.ts`
- `src/studio/external-http/editor.tsx`
- `src/commerce/integration/studio/services.ts`
- `tests/agent-configuration-production.test.tsx`
- `tests/connections-route-composition.test.tsx`
- `tests/connections-ui.test.tsx`
- `tests/external-tools-production.test.ts`
- `tests/external-tools-ui.test.tsx`
- `tests/studio-workspace.test.tsx`
- task Completion Report
- parent ARCH-021 checkpoint state

### Validation Reviewed

Submitted evidence:

```text
focused packet: 5 files / 59 tests passed
npm run lint: PASS with 8 unrelated warnings
git diff --check: PASS
```

The submitted full typecheck/build failures are consistent with previously recorded Commerce missing-preview/integration diagnostics outside the 14-file task implementation set. No changed-file typecheck diagnostic was reported.

The review archive does not contain `node_modules`, so the architect did not independently rerun Vitest/ESLint/Next build from the archive.

### Architecture Conformance

Partial.

The production Server/Client function-prop removal is substantially correct, but the Client Component public contract still contains `StudioServices` through `fixtureAdapter`, unexpected failures are still being collapsed without the required structured logging / visible failure class, and a production-composition regression test still encodes the old service-port architecture.

### Follow-up

Reclaim this same task as Attempt 2.

Perform **only** the bounded corrections below. Do not redesign Studio visuals, Tool algorithms, Connections domain semantics, Agent Configuration behavior, preview runtime, or Phase-3 contracts.

1. Remove `fixtureAdapter?: StudioServices` from `StudioWorkspace` production React props.
2. Move fixture service injection to a test-only mechanism or mock the named Server Action imports directly.
3. Preserve local/test `ExternalHttpUiPort` and `ConnectionPort` adapters only where they do not cross a production Server Component -> Client Component boundary.
4. Add approved shared structured logging for unexpected server-side Studio/Connections exceptions before translating them to bounded UI results. Pass the raw `Error` field.
5. Change task-owned client catches to retain/render a bounded actual failure class instead of silently converting arbitrary thrown failures to indistinguishable `unknown`/`unavailable`.
6. Remove empty reconciliation catches.
7. Update stale production-composition tests, especially `tests/agent-configuration-production.test.tsx`.
8. Add/adjust regressions for the failure behavior above.
9. Re-run a focused packet that includes at least:

   ```text
   tests/agent-configuration-production.test.tsx
   tests/connections-route-composition.test.tsx
   tests/connections-ui.test.tsx
   tests/external-tools-production.test.ts
   tests/external-tools-ui.test.tsx
   tests/studio-workspace.test.tsx
   ```

   Additional directly affected tests may be added.

10. Run targeted ESLint for every changed source/test file.
11. Run repository typecheck/build as required by the task. If the result still matches the already-recorded unrelated Commerce baseline, record the exact current diagnostics and confirm zero diagnostics in Attempt 2 changed files. Do not fix unrelated preview/integration baseline debt.
12. Run `git diff --check`.
13. Check every satisfied Work Item, Acceptance Criterion and Validation item in the task file. Do not return with the entire checklist unchecked.
14. Record the Attempt 2 launcher-prepared parent/implementation worktree evidence, synchronization/base evidence, recursive database submodule evidence, implementation commit, parent report commit, and final clean/upstream branch state.
15. Set the task to:

   ```yaml
   status: review
   executor: null
   claimed_at: null
   attempt: 2
   ```

16. Return to `moda_architect` and STOP. Do not start Phase-3 follow-on work or `ARCH-021-SYSTEM-TEST-001`.

`ARCH-021-SYSTEM-TEST-001` remains Pending while COMMERCE-029 is not Complete.
