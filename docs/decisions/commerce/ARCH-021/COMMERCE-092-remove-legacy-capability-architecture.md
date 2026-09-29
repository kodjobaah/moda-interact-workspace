---
id: ARCH-021-COMMERCE-092
architecture_id: ARCH-021
title: Remove the legacy Capability revision architecture
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 96
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-089
  - ARCH-021-COMMERCE-091
  - ARCH-021-BACKGROUND-002
enables:
  - ARCH-021-SYSTEM-TEST-003
created: 2026-09-29
updated: 2026-09-29
---

# Remove the legacy Capability revision architecture

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Delete the obsolete Capability draft/revision/binding UI, lifecycle, contracts, persistence adapters and fixtures after every supported authoring/runtime consumer has moved to the direct Feature/Capability/Tool model.

## Context

COMMERCE-088/089/090/091 and BACKGROUND-002 establish the replacement path. Temporary legacy code may have remained only to keep intermediate branches buildable while the backend and UI migrated independently.

This task is the subtractive completion gate. It must leave materially less Capability code, not a permanent compatibility layer around an obsolete domain model.

## Scope

Delete/reconcile obsolete Commerce files and symbols across:

```text
app/capabilities/page.tsx
app/capabilities/[id]/page.tsx
components/studio-workspace.tsx legacy Capability branches
src/studio/contracts.ts legacy CapabilityRevision/ToolBinding contracts
src/studio/server-actions.ts / server-services.ts legacy Capability actions
src/studio/testing/in-memory-studio-services.ts legacy Capability revision simulator
src/commerce/publication/ports.ts legacy CapabilityDraft/Revision/binding types
src/commerce/publication/lifecycle.ts obsolete Capability create-draft/update-draft/publish code
src/commerce/publication/validation.ts obsolete binding/config validation
src/commerce/publication/read-models.ts legacy revision views
src/commerce/integration/backend/publication-storage.ts obsolete capability-revision read/write handling
obsolete tests/fixtures/C20 setup that only support the removed model
navigation entries for standalone Capability authoring where no longer required
```

Retain release/runtime paths implemented by COMMERCE-089 and Feature authoring from COMMERCE-088/090/091.

## Out of Scope

- New functionality.
- Tool authoring cleanup unrelated to Capability architecture.
- Billing/subscription policy changes.
- Shared or Background changes already owned by their tasks.
- Broad Studio redesign unrelated to deleting obsolete Capability paths.

## Requirements

### R1 — remove standalone Capability authoring routes/surface

The primary authoring model is Feature-centric. Remove the standalone Capability list/editor routes and navigation when they exist only to support Capability revisions.

A deep/internal route may remain only if the new Feature-owned UX genuinely requires it; it must not expose the old editor/lifecycle.

### R2 — delete old lifecycle operations

Remove Capability operations/types whose semantics no longer exist:

```text
create Capability shell before Tool assignment
createDraft
updateDraft
publishRevision
clone Capability revision
Capability revision CAS/editor state
multi-Tool toolBindings[]
per-Capability promptTemplate/configuration
```

Do not retain deprecated wrappers or no-op methods.

### R3 — delete removed domain terminology from supported Commerce source

Supported Commerce source must contain no active Capability-domain use of:

```text
selectionBinding
BASE
RECOVERY_POLICY
CapabilityRevision
maxSearchResults
maxRecommendations
```

Generic runtime safety constants may exist under different generic names only where they are genuinely execution-safety concerns, not Capability configuration.

Historical architecture/task documents are not part of this source-code grep invariant.

### R4 — remove whole-publication Capability persistence machinery no longer needed

If the broad publication state/read-all/write-all adapter remains only for legacy Capability mutation after Tool/release migration, delete that Capability-specific handling.

Do not remove still-used release activation/rollback or Tool publication behavior merely for stylistic consistency.

### R5 — replace obsolete fixtures rather than translating them

Remove fixtures that manufacture `conversation_core` BASE Capabilities, Capability revisions, promptName identities or multi-binding configurations. Rewrite only the minimum deterministic fixtures required by supported Feature Capability/release/runtime tests.

### R6 — no unreachable compatibility branches

There must be one supported Feature Capability authoring path and one supported release/runtime path. Tests must prove old Capability routes/actions are absent or unreachable as designed.

## Work Items

- [x] Remove standalone legacy Capability routes/navigation/editor.
- [x] Remove CapabilityRevision/CapabilityDraft/ToolBinding Studio contracts.
- [x] Remove legacy Capability draft/update/publish Server Actions/services.
- [x] Remove obsolete publication lifecycle/validation/read-model code.
- [x] Remove obsolete publication-storage capability-revision handling.
- [x] Remove Capability `selectionBinding`/BASE/RECOVERY_POLICY branches from Commerce source.
- [x] Remove Capability-level `maxSearchResults` / `maxRecommendations` plumbing; retain only generically named implementation safety bounds where required.
- [x] Replace C20/in-memory/test fixtures that only model the old architecture.
- [x] Delete unreachable compatibility adapters introduced solely for staged migration.
- [x] Add source-level regression assertions/grep-style checks where useful to prevent legacy symbol reintroduction.

## Interfaces / Contracts

Consumes the accepted replacement paths from:

```text
ARCH-021-COMMERCE-088
ARCH-021-COMMERCE-089
ARCH-021-COMMERCE-090
ARCH-021-COMMERCE-091
ARCH-021-BACKGROUND-002
```

Produces no new runtime contract.

## Dependencies

- ARCH-021-COMMERCE-089
- ARCH-021-COMMERCE-091
- ARCH-021-BACKGROUND-002

## Enables

- ARCH-021-SYSTEM-TEST-003

## Acceptance Criteria

- [x] There is no supported standalone Capability revision editor/list workflow.
- [x] `createDraft`, `updateDraft`, Capability `publishRevision` and Capability clone flow are removed.
- [x] Commerce source no longer models `CapabilityRevision`/`CapabilityDraft`/multi-Tool bindings.
- [x] Commerce source no longer branches on Capability `selectionBinding`, BASE or RECOVERY_POLICY.
- [x] Capability-level `maxSearchResults` / `maxRecommendations` are absent; any remaining generic safety bounds are clearly execution-owned and not author-configurable.
- [x] No current fixture requires `conversation_core` as a BASE Capability.
- [x] The new Feature authoring and release/runtime focused suites remain green after deletion.
- [x] No temporary migration compatibility adapter remains reachable.

## Validation

- [x] focused Feature/Capability UI suites from COMMERCE-090/091
- [x] focused publication/backend suites from COMMERCE-089
- [ ] affected Studio integration/C20 suites after fixture replacement (disposable C20 database/Redis targets were not configured; see Completion Report)
- [x] targeted repository source search proving removed Capability-domain symbols are absent from supported source paths
- [x] targeted ESLint
- [x] changed-file TypeScript diagnostics / repository typecheck evidence per baseline policy
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP. Do not begin SYSTEM-TEST-003.

## Implementation Notes

Deletion is the purpose of this task. Do not preserve old code "just in case" during this pre-production breaking rollout.

## Completion Report

### Status

Ready for Architect Review

### Files Changed

Implementation commits on `task/ARCH-021-COMMERCE-092`:

```text
70a75dd Remove legacy Capability revision architecture
7b49eaa Guard against legacy Capability surface
```

```text
app/capabilities/[id]/page.tsx (deleted)
app/capabilities/page.tsx (deleted)
components/production-studio-page.tsx
components/studio-workspace.tsx
src/commerce/code-response/processor.ts
src/commerce/execution/renderer.ts
src/commerce/external-http/index.ts
src/commerce/external-preview/contracts.ts
src/commerce/external-preview/fixture-runner.ts
src/commerce/external-publication/contracts.ts
src/commerce/external-publication/index.ts
src/commerce/external-response/index.ts
src/commerce/integration/backend.ts
src/commerce/integration/backend/c20-test-fixture.ts
src/commerce/integration/backend/publication-storage.ts
src/commerce/integration/preview/adapters.ts
src/commerce/integration/studio/services.ts
src/commerce/mcp/authorization.ts
src/commerce/mcp/ports.ts
src/commerce/observability.ts
src/commerce/publication/lifecycle.ts
src/commerce/publication/ports.ts
src/commerce/publication/read-models.ts
src/commerce/publication/validation.ts
src/commerce/tool-authoring/external-live-test.ts
src/commerce/tool-authoring/policy-operation-live-test.ts
src/commerce/tool-authoring/shopify-admin-live-test.ts
src/studio/contracts.ts
src/studio/external-http/ports.ts
src/studio/server-actions.ts
src/studio/server-services.ts
src/studio/testing/in-memory-studio-services.ts
tests/admin-query-execution.test.ts
tests/backend-integration.test.ts
tests/backend-postgres-rehearsal.test.ts
tests/code-response-processor.test.ts
tests/commerce-lifecycle.test.ts
tests/definition-execution-mcp.test.ts
tests/definition-execution.test.ts
tests/external-availability.test.ts
tests/external-http-executor.test.ts
tests/external-publication.test.ts
tests/external-tools-ui.test.tsx
tests/external-wiring.test.ts
tests/feature-configuration-page.test.tsx
tests/fixtures/publication-store.ts
tests/legacy-capability-surface.test.ts
tests/local-external-mcp-diagnostic.test.ts
tests/mcp-authorization.test.ts
tests/mcp-compatibility.test.ts
tests/mcp-service.test.ts
tests/recommendation-contract.test.ts
tests/response-processing.test.ts
tests/result-template-optionality.test.ts
tests/result-template-renderer.test.ts
tests/studio-integration-c20.test.ts
tests/studio-integration.test.ts
tests/studio-services.test.ts
tests/studio-workspace.test.tsx
```

### Work Completed

Removed the standalone Capability pages and their Studio authoring/editor contracts, actions, services, and in-memory implementations. Removed Capability revision/draft/binding models and lifecycle, validation, read-model, persistence, audit, and telemetry handling while preserving Feature-owned Capability membership in release composition and the existing Tool/release/activation/rollback paths.

Replaced obsolete Capability-revision fixtures with direct Feature-owned Capability rows. Renamed the execution-owned safety bounds to `maxPolicyOutputItems` and `maxCollectionItems` without changing their values or control flow. Added `tests/legacy-capability-surface.test.ts` to guard route absence and obsolete Studio/publication lifecycle contracts.

Launcher evidence:

```text
Physical worktree isolation:
  canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
  parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-092
  parent branch: task/ARCH-021-COMMERCE-092
  implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-092
  implementation branch: task/ARCH-021-COMMERCE-092
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Recursive implementation submodules:
  git submodule sync --recursive: passed
  git submodule update --init --recursive: passed
  database submodule commit: e9fb60221f1532205650154dfff2aadb6270b14c
```

### Validation Results

Passed focused validation:

- `npm run test:arch021-tool-authoring-common`: 7 files, 80 tests passed.
- Lifecycle, external availability, and Studio integration: 3 files, 44 tests passed.
- Studio integration, external-tools UI, and Feature configuration UI: 3 files, 106 tests passed.
- `tests/legacy-capability-surface.test.ts`: 2 tests passed.
- Modified TypeScript/TSX ESLint: zero errors; one existing unused `_environment` warning in `tests/mcp-service.test.ts`.
- Targeted source audit found no removed legacy terms in supported `app`, `components`, `src`, and `tests` paths; route absence and `git diff --check` passed.
- Prisma Client generation completed successfully.
- Repository typecheck reported 40 errors across 13 unrelated/pre-existing files; no diagnostics remained in changed lifecycle, publication-adapter, or Studio-service files.

Limitations and unrelated failures:

- `tests/studio-workspace.test.tsx`: 7 failed, 5 passed; failures concern existing Tool-editor interactions, including the missing `Save draft` expectation, not Capability removal.
- A broader seven-file authoring/backend selection had 70 passing tests and 2 backend singleton-bootstrap setup failures caused by process-global backend initialization expectations.
- Real C20 integration was not run because `COMMERCE_TEST_DATABASE_URL`, `COMMERCE_TEST_REDIS_URL`, and `COMMERCE_C20_REDIS_NAMESPACE` disposable targets were not configured.

### Deviations

Added a focused legacy-surface regression test as a follow-up implementation commit. The real C20 integration validation remains unavailable without disposable database and Redis targets; no production or shared database was used.

### Assumptions

Feature persistence remains the owner of current Capability creation. Commerce publication reads those current rows for release resolution but no longer creates or mutates Capability revisions.

### Unresolved Issues

The C20 real-database/Redis integration remains unvalidated pending disposable test targets. The unrelated workspace UI, backend singleton-bootstrap, and repository-wide typecheck failures listed above remain outside this task's scope.

### Architectural Concerns

None identified during implementation; awaiting Architect Review.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is accepted.

The deletion was reviewed specifically for current-functionality regression risk. C092 removes the obsolete Capability revision/draft/multi-binding authoring architecture, but it does not remove the current Capability concept or the supported Feature/release/runtime flows.

The supported authoring path remains Feature-centric:

```text
/features
  -> /features/[id]
  -> /features/[id]/capabilities/new
  -> direct Feature + Tool Capability
```

`FeatureConfigurationScreen` remains the Feature configuration surface; `AddCapabilityScreen` creates exactly one direct Feature/Tool Capability through `createFeatureCapability`. The deleted `/capabilities` list/editor routes and the removed `createDraft` / `updateDraft` / Capability `publishRevision` operations belonged only to the superseded Capability-revision model.

Current Tool functionality remains intact: Tool creation, draft update, Tool publication, External/Shopify authoring, live-Test and Result Template paths are still present. The reported `studio-workspace.test.tsx` failures exercise stale Tool-editor expectations (for example expecting `Save draft` outside the current Review-oriented authoring flow) and do not reveal a removed Capability replacement path.

Current release/runtime functionality also remains intact:

- release composition still calls `listReleaseCapabilities`;
- current direct Capability rows retain `featureId` + `toolId`;
- `createRelease` resolves the latest PUBLISHED Tool revision for each selected Capability and pins that exact `toolRevisionId`;
- current Feature Behaviour is snapshotted once per Feature into the immutable release;
- release activation and rollback remain unchanged;
- persisted release membership still carries Capability, Feature, Tool and pinned Tool-revision identity;
- MCP authorization/runtime manifest handling still consumes Capability membership and the pinned release data.

No supported caller remains for the removed standalone Capability revision routes/actions/contracts, and the dedicated legacy-surface regression proves those obsolete surfaces are absent.

The replacement dependencies required by this subtraction gate are all Complete: COMMERCE-089, COMMERCE-091 and BACKGROUND-002. DATABASE-003, SHARED-002, COMMERCE-088 and COMMERCE-090 are also Complete, so the simplified Feature/Capability architecture is fully materialized before deletion.

The real disposable C20 database/Redis rehearsal was not run because disposable targets were not configured. This remains a validation limitation and is not represented as passed. It does not reveal a source-level regression in the inspected C092 changes, and terminal SYSTEM-TEST-003 is promoted to Ready to perform the end-to-end validation of direct Capability creation, Feature Behaviour sharing, immutable Tool-revision pinning, Feature Behaviour snapshots and absence of the legacy revision/binding model.

### Reviewed Files

- `app/capabilities/page.tsx` (deleted)
- `app/capabilities/[id]/page.tsx` (deleted)
- `app/features/page.tsx`
- `app/features/[id]/page.tsx`
- `app/features/[id]/capabilities/new/page.tsx`
- `components/production-studio-page.tsx`
- `components/studio-shell.tsx`
- `components/studio-workspace.tsx`
- `src/studio/features/contracts.ts`
- `src/studio/features/persistence.ts`
- `src/studio/features/services.ts`
- `src/studio/features/add-capability/add-capability-screen.tsx`
- `src/studio/server-actions.ts`
- `src/studio/server-services.ts`
- `src/commerce/publication/ports.ts`
- `src/commerce/publication/lifecycle.ts`
- `src/commerce/publication/read-models.ts`
- `src/commerce/integration/backend/publication-storage.ts`
- `src/commerce/integration/backend.ts`
- `src/commerce/mcp/authorization.ts`
- `src/commerce/mcp/service.ts`
- `tests/legacy-capability-surface.test.ts`
- affected focused Feature/release/runtime tests listed in the Completion Report

### Validation Reviewed

- `npm run test:arch021-tool-authoring-common`: 80 tests passed.
- Lifecycle/external-availability/Studio integration packet: 44 tests passed.
- Studio integration/External Tools UI/Feature configuration packet: 106 tests passed.
- Legacy Capability surface guard: 2 tests passed.
- Targeted ESLint: zero errors; one documented existing warning.
- Targeted removed-symbol/source audit: passed.
- Prisma Client generation: passed.
- `git diff --check`: passed.
- Repository typecheck: 40 diagnostics in 13 unrelated/pre-existing files; no diagnostics remain in the C092-changed lifecycle/publication/Studio-service files.
- Broader `studio-workspace.test.tsx`: 7 existing Tool-editor expectation failures and 5 passes; inspected failures do not map to removed Capability replacement behavior.
- Broader backend selection: 70 passes with 2 existing process-global backend bootstrap failures.
- Real disposable C20 DB/Redis integration: not run because the required disposable targets were not configured; explicitly deferred to integrated validation rather than recorded as passed.

### Architecture Conformance

Conforms.

C092 completes the pre-production breaking removal of the obsolete Capability revision architecture while preserving the accepted direct Feature -> Capability -> Tool authoring model and immutable release/runtime composition. The current Capability entity remains in use; only its superseded draft/revision/binding lifecycle is removed.

### Follow-up

ARCH-021-COMMERCE-092 is Complete.

ARCH-021-SYSTEM-TEST-003 is promoted to Ready because every declared implementation/publication dependency is now Complete. The developer may manually exercise the completed Feature flow before invoking the terminal system test.
