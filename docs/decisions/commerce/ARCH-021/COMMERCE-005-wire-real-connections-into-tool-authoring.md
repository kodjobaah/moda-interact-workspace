---
id: ARCH-021-COMMERCE-005
architecture_id: ARCH-021
title: Wire real external connections into Tool authoring
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 40
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-001
  - ARCH-021-COMMERCE-004
  - ARCH-020-COMMERCE-023
enables:
  - ARCH-021-COMMERCE-006
created: 2026-09-23
updated: 2026-09-23
---

# Wire real external connections into Tool authoring

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Make the production U06 external-tool editor list and bind real persisted external connection revisions while retaining deterministic synthetic sample processing only as a temporary Phase 1/automated-test concern.

## Context

`ExternalHttpEditor` already authors an `EXTERNAL_HTTP` definition and binds an immutable `connectionRevisionId`, but `ProductionStudioPage` does not supply an `externalHttpPort`. The only concrete `ExternalHttpUiPort` factory currently contains synthetic connection/revision records.

Phase 1 must fix the **connection-authoring source** now. Live provider execution is deliberately Phase 4, so this task must not prematurely replace sample execution with network calls.

The selected shop context from ARCH-021-COMMERCE-004 is carried through navigation and made available for later per-shop testing, but selecting a connection revision remains independent of whether a credential is currently configured for that shop.

## Scope

- Supply production Tool authoring with real persisted `ConnectionView` / `ConnectionRevisionView` data from ARCH-021-COMMERCE-001.
- Refactor the current external-authoring port if necessary so production connection catalogue data is not coupled to fixture connection records.
- Pass the production external-authoring dependency into `ProductionStudioPage -> StudioWorkspace -> ExternalHttpEditor`.
- Preserve immutable connection revision selection in saved tool definitions.
- Preserve/manage `returnTo` and selected `shopId` when navigating from Tool authoring to Connections and back.
- Keep current synthetic response samples/processors explicitly separated from the real connection catalogue until Phase 4.

## Out of Scope

- Making an external HTTP provider request.
- Decrypting credentials during Tool authoring.
- Requiring a PER_SHOP credential merely to save a draft definition.
- Shopify tool execution.
- JavaScript response-panel installation (ARCH-021-COMMERCE-006).
- Prompt/model configuration.
- Changing Shared `EXTERNAL_HTTP` definition shape.

## Requirements

- Production connection/revision choices must come from persisted lifecycle data, never the hard-coded `connection_fixture` / `connection_revision_fixture` records.
- The editor continues to save the exact immutable `connectionRevisionId` in `CommerceToolDefinition.execution`.
- Disabled/missing/stale connections must be presented safely and must not be replaced silently by another revision. Existing publication/runtime validation remains authoritative for deployability.
- A previously selected revision remains selected when editing an existing draft even if it is not the newest revision.
- “Manage connections” navigation must preserve the Tool return target and current `shopId`.
- Any remaining synthetic sample fixtures must be clearly test/preview-only and must not masquerade as connection/provider data.

## Work Items

- [ ] Separate real connection catalogue data from the synthetic external sample fixture factory/port as needed.
- [ ] Load real Connection/Revision views for production Tool authoring through the ARCH-021-COMMERCE-001 server boundary.
- [ ] Install the resulting external-authoring port/data in `ProductionStudioPage` / `StudioWorkspace`.
- [ ] Preserve exact saved revision selection and missing/stale revision presentation.
- [ ] Preserve `returnTo` plus selected `shopId` through “Manage connections” navigation.
- [ ] Add regression tests proving production Tool authoring does not show `connection_fixture` and uses persisted connection ids/revision ids.
- [ ] Keep existing fixture-based editor tests available by injection.

## Interfaces / Contracts

Consumes:

- production ConnectionPort/data from ARCH-021-COMMERCE-001
- selected-shop navigation context from ARCH-021-COMMERCE-004
- existing `ExternalHttpEditor` / `ExternalHttpUiPort` from ARCH-020-COMMERCE-023
- existing Shared `ConnectionView` / `ConnectionRevisionView` / `CommerceToolDefinition`

Produces:

- production-backed external connection selection in U06 Tool authoring.

No Shared/Database contract change is introduced.

## Dependencies

- ARCH-021-COMMERCE-001
- ARCH-021-COMMERCE-004
- ARCH-020-COMMERCE-023

## Enables

- ARCH-021-COMMERCE-006

## Acceptance Criteria

- [ ] Production external Tool authoring lists real persisted connections/revisions.
- [ ] Saving a draft preserves the exact selected immutable `connectionRevisionId`.
- [ ] Existing drafts never silently jump to the latest revision.
- [ ] Production Tool authoring no longer depends on the synthetic connection/revision fixture records.
- [ ] Connection-management round trip preserves the Tool return target and selected shop context.
- [ ] No provider request or credential decryption occurs from merely opening/editing the Tool authoring screen.

## Validation

- [ ] focused external Tool authoring composition tests with real/injected persisted connection data
- [ ] existing external-tools UI tests
- [ ] relevant Studio workspace/integration tests
- [ ] targeted lint/typecheck for changed files
- [ ] `git diff --check`

No live third-party request is permitted.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin ARCH-021-COMMERCE-006.

## Implementation Notes

Do not solve Phase 4 early. Synthetic response samples can remain for deterministic code/visual authoring validation, but production **connection metadata** must be real after this task.

## Completion Report

### Status

Ready for Review

### Files Changed

Implementation commit: `1370a87` (pushed to `task/ARCH-021-COMMERCE-005`)

- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `src/studio/external-http/ports.ts`
- `tests/external-tools-ui.test.tsx`
- `tests/external-tools-production.test.ts`

### Work Completed

- Production `/tools` composition now reads persisted `ConnectionView` and `ConnectionRevisionView` values through the accepted ARCH-021-COMMERCE-001 `listConnections` server action and installs a production external-authoring port.
- Synthetic response samples/processors remain available through the explicitly named sample/fixture factories; production connection metadata no longer comes from `connection_fixture` or `connection_revision_fixture`.
- Tool authoring continues to save the exact immutable `connectionRevisionId`, including when editing an older draft revision; no credential status or secret resolution is performed while opening the editor.
- Manage-connections navigation preserves the selected tool revision return target and selected `shopId`.
- Added persisted-catalogue and selected-shop handoff regressions while retaining existing injected fixture-based editor coverage.

### Validation Results

- `npm exec vitest run tests/external-tools-ui.test.tsx tests/external-tools-production.test.ts` -> 2 files, 9 tests passed.
- Focused integration run: `npm exec vitest run tests/connections-production.test.ts tests/connections-server-actions.test.ts tests/connections-navigation.test.ts tests/selected-shop-context.test.ts tests/selected-shop-route.test.tsx tests/selected-shop-navigation.test.tsx tests/connection-lifecycle.test.ts tests/external-credentials.test.ts tests/external-tools-ui.test.tsx tests/external-tools-production.test.ts` -> 45 passed, 2 pre-existing baseline failures: the lifecycle development-bypass fixture failure documented by ARCH-021-COMMERCE-001, and the existing selected-shop route composition failure in `tests/selected-shop-route.test.tsx`.
- `npm exec eslint components/production-studio-page.tsx components/studio-workspace.tsx src/studio/external-http/ports.ts tests/external-tools-ui.test.tsx tests/external-tools-production.test.ts` -> passed with no warnings/errors.
- `npm run typecheck` -> non-zero on existing diagnostics in unrelated integration/publication-storage/studio-service files; no diagnostics referenced changed files.
- `git diff --check` -> passed.
- No live third-party calls were launched.

### Deviations

- The required focused integration run retains the two documented baseline failures above; neither is in the changed source path.

### Assumptions

- The accepted `listConnections` server action is the authoritative authenticated production read boundary and its bounded result is sufficient for the U06 catalogue; unavailable reads produce an empty catalogue without fixture fallback.

### Unresolved Issues

- Developer/architect follow-up remains for the two pre-existing focused-suite failures before treating those suites as fully green.

### Architectural Concerns

None. Phase 4 provider execution and credential decryption remain out of scope.

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
