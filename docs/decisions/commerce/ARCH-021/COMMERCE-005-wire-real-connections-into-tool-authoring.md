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
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 2
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

- [x] Separate real connection catalogue data from the synthetic external sample fixture factory/port as needed.
- [x] Load real Connection/Revision views for production Tool authoring through the ARCH-021-COMMERCE-001 server boundary.
- [x] Install the resulting external-authoring port/data in `ProductionStudioPage` / `StudioWorkspace`.
- [x] Preserve exact saved revision selection and missing/stale revision presentation.
- [x] Preserve `returnTo` plus selected `shopId` through “Manage connections” navigation.
- [x] Add regression tests proving production Tool authoring does not show `connection_fixture` and uses persisted connection ids/revision ids.
- [x] Keep existing fixture-based editor tests available by injection.

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

- [x] Production external Tool authoring lists real persisted connections/revisions.
- [x] Saving a draft preserves the exact selected immutable `connectionRevisionId`.
- [x] Existing drafts never silently jump to the latest revision.
- [x] Production Tool authoring no longer depends on the synthetic connection/revision fixture records.
- [x] Connection-management round trip preserves the Tool return target and selected shop context.
- [x] No provider request or credential decryption occurs from merely opening/editing the Tool authoring screen.

## Validation

- [x] focused external Tool authoring composition tests with real/injected persisted connection data
- [x] existing external-tools UI tests
- [x] relevant Studio workspace/integration tests
- [x] targeted lint/typecheck for changed files
- [x] `git diff --check`

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

### Attempt 2 Correction Report

#### A1-R1 — implemented

- `app/connections/page.tsx`: collapsed the merged composition to one `ConnectionsRouteClient`, retained server-validated `shopSelection`, preserved `search`, `cursor`, `enabled`, and passed validated `returnTo`; added `returnTo?: string` to `searchParams`.
- `app/connections/[id]/page.tsx`: applied the same single-client composition for U16 while retaining `detailId`, all list state, validated `shopSelection`, and validated `returnTo`; added `returnTo?: string` to `searchParams`.
- `tests/selected-shop-route.test.tsx`: now proves detail and list direct-entry composition each expose one route client, preserve selected-shop/query state, retain detail identity, and reject an unsafe return target.
- Focused proof: `npm exec vitest run tests/selected-shop-route.test.tsx tests/connections-route-composition.test.tsx` -> 2 files, 4 tests passed.

#### A1-R2 — implemented

- Re-ran the reviewed Tool authoring and Connections integration set: 10 files, 49 tests total, 48 passed and 1 failed. The single failure is the unchanged lifecycle development-bypass fixture failure at `tests/connection-lifecycle.test.ts:215`, previously documented by ARCH-021-COMMERCE-001; the selected-shop route failure is resolved and is no longer classified as baseline.
- Targeted ESLint over both corrected route files, the route regression, and all Attempt 1 changed files passed with no warnings/errors.
- `npm run typecheck` remains non-zero only on pre-existing unrelated diagnostics in `src/commerce/integration/backend.ts`, `src/commerce/integration/backend/publication-storage.ts`, `src/commerce/integration/studio/services.ts`, and related integration tests; no diagnostic references the changed route or Tool-authoring files.
- `git diff --check` passed.
- No live third-party requests were launched; opening/editing Tool authoring still performs no provider request or credential decryption.

#### Prepared workflow evidence

- Launcher-prepared parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-005`.
- Launcher-prepared implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-005`.
- Mirrored branch: `task/ARCH-021-COMMERCE-005` in both repositories.
- The deterministic launcher completed branch synchronization/fast-forward preparation and recursive submodule initialization before this Attempt 2 handoff; no startup re-synchronization or submodule mutation was performed during implementation.

#### Remaining gaps

- The accepted lifecycle development-bypass fixture failure remains outside this task's changed path and is retained as the only focused-suite failure.
- The repository-wide typecheck remains blocked by the pre-existing unrelated diagnostics listed above.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 (`9033069`; parent report `1131be5`) satisfies the complete Attempt 1 correction contract and the original COMMERCE-005 acceptance contract.

The production Tool-authoring implementation from Attempt 1 remains architecture-conformant: `/tools` obtains persisted `ConnectionView` / `ConnectionRevisionView` metadata through the accepted COMMERCE-001 authenticated server boundary, production composition no longer installs the synthetic `connection_fixture` / `connection_revision_fixture` catalogue records, and saved Tool definitions continue to retain the exact immutable `connectionRevisionId`. Synthetic response samples remain isolated to deterministic authoring/test behaviour and no live provider request or credential decryption is introduced.

Attempt 2 correctly reconciles the merged Connections dependency state. Both `/connections` and `/connections/[id]` now compose exactly one `ConnectionsRouteClient` while preserving the accepted COMMERCE-004 `StudioShell.shopSelection` context and the COMMERCE-002 validated `returnTo` consumer. The list route retains `search`, `cursor` and `enabled`; the detail route additionally retains `detailId`. Both route-local search parameter contracts now declare `returnTo?: string`.

The selected-shop route regression now proves direct-entry restoration of shop context and a valid Tool return target on U16, and proves the list route preserves query state while rejecting an unsafe external-style return target. The focused route proof is green. The only remaining focused-suite failure reported for Attempt 2 is the previously documented lifecycle development-bypass fixture failure; the selected-shop regression introduced by the prior merge artifact is resolved and is no longer classified as baseline.

Attempt 1 -> Attempt 2 comparison shows only the requested two route corrections, the selected-shop route regression update, the task report, and ignored `tsconfig.tsbuildinfo` output. No unrelated production implementation drift was introduced. The Completion Report records the launcher-prepared parent and implementation worktrees, mirrored branch, synchronization and recursive-submodule preparation evidence.

### Reviewed Files

- `moda-interact-commerce/components/production-studio-page.tsx`
- `moda-interact-commerce/components/studio-workspace.tsx`
- `moda-interact-commerce/src/studio/external-http/ports.ts`
- `moda-interact-commerce/src/studio/external-http/editor.tsx`
- `moda-interact-commerce/src/studio/connections/server-actions.ts`
- `moda-interact-commerce/src/studio/connections/navigation.ts`
- `moda-interact-commerce/src/studio/connections/connections-route-client.tsx`
- `moda-interact-commerce/app/connections/page.tsx`
- `moda-interact-commerce/app/connections/[id]/page.tsx`
- `moda-interact-commerce/tests/external-tools-production.test.ts`
- `moda-interact-commerce/tests/external-tools-ui.test.tsx`
- `moda-interact-commerce/tests/selected-shop-route.test.tsx`
- `moda-interact-commerce/tests/connections-route-composition.test.tsx`

### Validation Reviewed

- Reported focused route validation: 2 files / 4 tests passed.
- Reported relevant Tool-authoring/Connections integration set: 48 passed / 1 previously documented lifecycle development-bypass fixture failure.
- Reported targeted ESLint: passed.
- Reported implementation `git diff --check`: passed.
- Reported repository typecheck remains non-zero only on existing unrelated integration/publication diagnostics; no changed route or Tool-authoring diagnostic was reported.
- No live third-party request was made during the submitted validation.
- Architect static review confirms each Connections route contains exactly one `ConnectionsRouteClient`, preserves server-validated `shopSelection`, and passes only `validateConnectionsReturnTo(query.returnTo)` to the route client.
- Architect Attempt 1 -> Attempt 2 comparison found only the requested route/test corrections plus ignored `tsconfig.tsbuildinfo`; `.gitignore` excludes `*.tsbuildinfo`.
- The supplied review archive contains no `node_modules`, so the architect did not independently rerun the Node/Vitest commands in the review container.

### Architecture Conformance

Conformant. Production U06 Tool authoring now consumes persisted immutable connection/revision metadata through the accepted server boundary, keeps fixture/sample behaviour injectable and non-provider-facing, preserves the exact revision binding, and round-trips through U15/U16 with both selected-shop and validated return context intact. Attempt 2 restores the accepted single-client Connections composition without changing provider execution, credential semantics, Shared contracts or Database contracts.

### Follow-up

ARCH-021-COMMERCE-005 is accepted Complete. ARCH-021-COMMERCE-006 is now Ready because COMMERCE-005 and its ARCH-020-COMMERCE-026/027/031 prerequisites are Complete. COMMERCE-006 is the sole remaining Phase 1 implementation task; do not begin Phase 2 work until Phase 1 is architect-reconciled after COMMERCE-006 review.
