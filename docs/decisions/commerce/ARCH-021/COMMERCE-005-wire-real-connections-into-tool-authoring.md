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

Changes Requested — Attempt 1.

### Review Notes

Reviewed by `moda_architect` against the ARCH-021-COMMERCE-005 task contract, ARCH-021 Phase 1, the supplied implementation snapshot, implementation handoff `1370a87`, and parent report handoff `351c064`.

The COMMERCE-005 Tool-authoring implementation is directionally conformant: production Tool composition obtains persisted `ConnectionView` / `ConnectionRevisionView` metadata through the accepted COMMERCE-001 server boundary; the production external-authoring port no longer installs `connection_fixture` / `connection_revision_fixture`; synthetic response samples/processors remain separate and no live provider call or credential decryption was introduced; and the Tool-side Manage connections handoff carries the exact tool-revision return target plus selected-shop context.

Attempt 1 is not accepted because the submitted integrated source contains a directly relevant U06 -> U15/U16 -> U06 navigation regression in the accepted Connections dependency. Both `app/connections/page.tsx` and `app/connections/[id]/page.tsx` currently render two `ConnectionsRouteClient` instances inside one `StudioShell`: one instance without `returnTo`, followed by another with validated `returnTo`. This is a merge/integration artifact, not an accepted baseline. It duplicates the Connections surface/read lifecycle and breaks the selected-shop route regression because `StudioShell.props.children` is now an array rather than the one accepted route client.

The Completion Report itself records `tests/selected-shop-route.test.tsx` as an existing baseline failure. That classification is rejected. The accepted COMMERCE-004 source had one Connections route client and the selected-shop direct-entry contract was accepted on that basis. A newly merged failure in the same ARCH-021 navigation path cannot be waived as unrelated baseline debt. The existing lifecycle development-bypass failure may continue to be referenced separately if it remains byte-for-byte unchanged.

The corrections below are the complete Attempt 2 contract. Keep the COMMERCE-005 Tool-authoring design intact unless a change is required to preserve these accepted navigation semantics.

#### A1-R1 — collapse the merged Connections route composition to one client

**Source and focused-test changes required.**

Correct both:

- `app/connections/page.tsx`
- `app/connections/[id]/page.tsx`

Each route must render exactly one `ConnectionsRouteClient` under the existing `StudioShell`. The merged result must preserve both accepted dependency behaviours simultaneously:

```text
StudioShell.shopSelection = server-validated selected-shop context
ConnectionsRouteClient.returnTo = validateConnectionsReturnTo(query.returnTo)
```

The sole route client must also retain the existing `search`, `cursor`, `enabled` state and `detailId` on U16. Do not choose one dependency side wholesale and do not render two clients.

Because these route annotations are now being corrected, add `returnTo?: string` to the local `searchParams` type for both pages so the runtime contract and TypeScript annotation agree. This is the narrow hygiene item already identified during COMMERCE-002 review; no broader typecheck cleanup is assigned.

Required focused proof:

```text
/connections direct entry
  -> exactly one ConnectionsRouteClient
  -> validated shopSelection remains on StudioShell
  -> validated returnTo reaches the sole client
  -> search/cursor/enabled preserved

/connections/<id> direct entry
  -> exactly one ConnectionsRouteClient
  -> validated shopSelection remains on StudioShell
  -> validated returnTo reaches the sole client
  -> detailId + search/cursor/enabled preserved
```

The existing `tests/selected-shop-route.test.tsx` must return green. Add or adjust a focused route-composition regression so both list and detail routes fail if duplicate route clients are reintroduced.

#### A1-R2 — rerun the COMMERCE-005 navigation/integration proof and report baseline truthfully

**Validation/report correction required; source changes only if the focused proof exposes another task-scoped defect.**

After A1-R1, rerun the focused COMMERCE-005 authoring tests and the relevant Connections/selected-shop integration set. The Tool -> Connections -> Tool round trip must preserve the exact tool revision, validated `returnTo`, and selected `shopId` without duplicated Connections composition.

Do not report the current selected-shop route failure as baseline. If the lifecycle development-bypass failure remains unchanged, identify it by its existing accepted/baseline context and keep it separate from task-scoped results.

Reconcile the task Work Items, Acceptance Criteria and Validation checkboxes truthfully before returning to review. The Completion Report must also record the launcher-prepared parent/implementation worktrees, branch synchronization and recursive submodule evidence required by the task workflow. This evidence/reporting correction does not require artificial implementation churn.

### Reviewed Files

- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `src/studio/external-http/ports.ts`
- `src/studio/external-http/editor.tsx`
- `src/studio/connections/server-actions.ts`
- `src/studio/connections/production.ts`
- `src/studio/connections/navigation.ts`
- `src/studio/connections/connections-route-client.tsx`
- `src/studio/connections/connections-ui.tsx`
- `app/connections/page.tsx`
- `app/connections/[id]/page.tsx`
- `tests/external-tools-production.test.ts`
- `tests/external-tools-ui.test.tsx`
- `tests/selected-shop-route.test.tsx`
- `tests/connections-route-composition.test.tsx`
- `docs/decisions/commerce/ARCH-021/COMMERCE-002-switch-connections-routes-to-production-port.md`
- `docs/decisions/commerce/ARCH-021/COMMERCE-004-add-studio-selected-shop-context.md`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

### Validation Reviewed

- Submitted focused external Tool authoring suite: 9 passed.
- Submitted integration set: 45 passed / 2 failed. The lifecycle development-bypass failure is previously known; the selected-shop route failure is directly explained by the duplicate route-client merge artifact and is blocking.
- Submitted targeted ESLint: passed.
- Submitted `git diff --check`: passed.
- Submitted repository typecheck remains non-zero on existing broad diagnostics; architect source inspection additionally confirms the two Connections route annotations read `query.returnTo` without declaring `returnTo?: string`, the narrow hygiene item already noted in the accepted COMMERCE-002 review.
- The supplied archive does not contain `node_modules`, so the architect did not rerun the Node test commands in the review container.

### Architecture Conformance

The COMMERCE-005 Tool-authoring changes are otherwise aligned with Phase 1, but the submitted integrated branch is not currently architecture-conformant because accepted U15/U16 and selected-shop route composition has regressed. Acceptance requires one composed production Connections client carrying both selected-shop and validated-return context.

### Follow-up

Return the same task through the normal `/moda-task ARCH-021-COMMERCE-005` path for Attempt 2. Preserve `attempt: 1` until the next authorized claim increments it. ARCH-021-COMMERCE-006 remains dependency-gated until COMMERCE-005 is architect-accepted Complete.
