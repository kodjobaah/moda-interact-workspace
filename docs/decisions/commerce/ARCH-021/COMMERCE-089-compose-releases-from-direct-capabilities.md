---
id: ARCH-021-COMMERCE-089
architecture_id: ARCH-021
title: Compose releases and runtime manifests from direct Capabilities
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 92
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-DATABASE-003
  - ARCH-021-SHARED-002
  - ARCH-021-COMMERCE-088
enables:
  - ARCH-021-BACKGROUND-002
  - ARCH-021-COMMERCE-092
created: 2026-09-29
updated: 2026-09-29
---

# Compose releases and runtime manifests from direct Capabilities

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Replace Capability-revision release composition and runtime resolution with direct Capability membership, release-time Tool revision pinning and one immutable Feature behaviour snapshot per represented Feature.

## Context

Current release/runtime code walks `CommerceCapabilityRevision`, parses `toolBindings[]`, reads Capability configuration limits, handles `BASE`/`RECOVERY_POLICY` special cases and generates per-Capability prompt identities.

DATABASE-003 and SHARED-001/002 establish a smaller model. Release creation is now the versioning boundary: authors choose a Tool identity when creating the Capability, while a release freezes the exact published Tool revision and the Feature's current behaviour text.

This task is the Commerce producer/runtime cutover. It must not preserve the old revision model behind adapters.

## Scope

Primary areas include:

```text
package.json / lockfile                         # consume published SHARED-002 version
database/                                       # accepted DATABASE-003 gitlink
src/commerce/publication/* release creation/read models
src/commerce/integration/backend.ts
src/commerce/integration/backend/publication-storage.ts where still relevant
src/commerce/integration/studio/services.ts release methods/read models
src/studio release contracts/actions required to compile current release UI
focused lifecycle/backend/MCP/Studio tests
C20/integration fixture code that constructs releases/manifests
```

## Out of Scope

- New Feature/Capability creation UI.
- Background consumer changes.
- Billing/subscription entitlement policy redesign.
- Agent Configuration model/prompt runtime cutover beyond this Feature behaviour composition.
- Final removal of every obsolete UI/compatibility file; COMMERCE-092 is the deletion gate.

## Requirements

### R1 — consume canonical new contracts

Update to the exact `@modainteract/moda-interact-shared` version published by SHARED-002 and the accepted DATABASE-003 database submodule.

Do not copy Shared manifest schemas/types locally.

### R2 — release input names Capability identities, not Capability revisions

Release creation accepts ordered Capability IDs/positions. It must not accept or expose `capabilityRevisionId`.

Before writing the release, resolve every selected Capability's current immutable `toolId` and choose the highest `revisionNumber` PUBLISHED revision for that Tool using deterministic ordering.

If any selected Capability has no currently published Tool revision, release creation fails before durable release rows are written.

### R3 — snapshot Feature behaviour once per Feature

For every distinct Feature represented by the ordered release Capabilities, snapshot the current `behaviourPrompt` into exactly one release Feature row. An absent current Feature configuration resolves to the documented blank behaviour prompt.

Later edits to the current Feature behaviour must not change existing releases.

### R4 — runtime manifest derives from immutable release rows

Generate the Shared manifest directly from:

```text
CommerceRelease
CommerceReleaseFeature snapshots
CommerceReleaseCapability members
CommerceCapability stable identity/Feature
pinned CommerceToolRevision
```

Do not query `CommerceCapabilityRevision`, parse `toolBindings[]`, synthesize Capability prompt names or read Capability configuration.

### R5 — no BASE/RECOVERY_POLICY runtime branches

Remove producer-side branches based on `selectionBinding`, `conversation_core` or `RECOVERY_POLICY`.

All release Capabilities are ordinary Feature capabilities. Runtime eligibility may still filter them using Feature facts, but the authoring/release model has no Capability type discriminator.

A valid manifest may contain zero selected capabilities after Feature eligibility filtering.

### R6 — preserve Feature eligibility as a separate runtime concern

Existing plan/subscription/preference/recovery state must not leak back into Capability authoring, but runtime Feature eligibility may continue to determine which release Capabilities are active for a shop.

Express eligibility only through the Capability's required `featureId`; do not recreate a Capability binding enum.

This task must not redesign billing policy.

### R7 — remove capability-owned result limits from runtime composition

Delete calculation/propagation of Capability `maxSearchResults` / `maxRecommendations`.

Where generic execution/result processing still requires safety bounds, use implementation-owned constants or generic execution-limit names that are not sourced from Capability data and are not exposed as Capability configuration.

### R8 — one Tool descriptor per Capability

Build exactly one Tool descriptor for each selected Capability from its release-pinned Tool revision.

When several capabilities reuse one Tool revision, Shared deduplication/grant provenance must still produce one granted Tool with all applicable Capability keys.

### R9 — release replay/immutability remains deterministic

Preserve existing create/activate/rollback authorization, exact operation replay and immutable release semantics while changing the composition payload.

Do not make current Feature behaviour or current Tool publication state affect an already-created release.

## Work Items

- [x] Consume the SHARED-002 package version and DATABASE-003 schema.
- [x] Replace release request/read models that carry Capability revision IDs.
- [x] Resolve one exact latest PUBLISHED Tool revision per selected Capability at release creation.
- [x] Persist one immutable Feature behaviour snapshot per represented Feature.
- [x] Build the new Shared manifest from direct release rows.
- [x] Remove `selectionBinding`, `conversation_core` and RECOVERY_POLICY producer branches.
- [x] Remove per-Capability prompt/configuration/toolBindings resolution.
- [x] Remove Capability-derived `maxSearchResults` / `maxRecommendations` calculation.
- [x] Update release activation/rollback/inspection paths for the new member model.
- [x] Update C20/backend/MCP deterministic fixtures to the direct model.
- [x] Add release immutability regression tests for later Tool publication and Feature-prompt edits.
- [x] Add zero-selected-capability and reused-Tool manifest tests.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-DATABASE-003 database model
ARCH-021-SHARED-002 published Shared Commerce contract
ARCH-021-COMMERCE-088 direct Capability records
```

Produces manifests consumed by ARCH-021-BACKGROUND-002.

## Dependencies

- ARCH-021-DATABASE-003
- ARCH-021-SHARED-002
- ARCH-021-COMMERCE-088

## Enables

- ARCH-021-BACKGROUND-002
- ARCH-021-COMMERCE-092

## Acceptance Criteria

- [x] Release creation contains no Capability revision ID input/output.
- [x] Each release Capability pins exactly one PUBLISHED Tool revision belonging to the Capability's assigned Tool.
- [x] Each represented Feature has exactly one immutable behaviour snapshot per release.
- [x] Changing current Feature behaviour after release creation leaves the old manifest unchanged.
- [x] Publishing a newer Tool revision after release creation leaves the old manifest pinned to the older exact revision.
- [x] Runtime manifest production does not query/parse Capability revisions, bindings or configuration.
- [x] No producer branch depends on BASE/RECOVERY_POLICY/`conversation_core`.
- [x] Runtime Feature eligibility remains separate from authoring and is expressed through `featureId` only.
- [x] No Capability-derived `maxSearchResults` / `maxRecommendations` remain.
- [x] Zero selected capabilities is handled deterministically without inventing a base Capability.
- [x] Reused Tool identities deduplicate correctly in the grant contract.

## Validation

- [x] focused publication lifecycle tests
- [x] focused backend integration tests (C089-focused cases pass; two unrelated process-global backend expectation cases fail)
- [x] focused MCP manifest/inspection tests
- [x] focused Studio release service tests
- [x] deterministic C20 fixture tests affected by the changed model
- [x] targeted ESLint
- [x] changed-file TypeScript diagnostics / repository typecheck evidence per baseline policy
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP. Do not modify Background or begin final legacy deletion.

## Implementation Notes

This task may make the current release UI use Capability IDs instead of revision IDs where necessary for compilation and functional parity, but it must not implement the new Feature Capability authoring wizard owned by COMMERCE-090/091.

## Completion Report

### Status

Ready for Architect Review

### Files Changed

Exact implementation delta on the final synchronized Commerce task branch (`origin/main...1a325609cb08ba00324ace611121bc5b3104d272`):

```text
components/studio-workspace.tsx
package-lock.json
package.json
src/commerce/external-response/index.ts
src/commerce/integration/backend.ts
src/commerce/integration/backend/c20-test-fixture.ts
src/commerce/integration/backend/publication-storage.ts
src/commerce/integration/preview/adapters.ts
src/commerce/integration/studio/services.ts
src/commerce/mcp/authorization.ts
src/commerce/mcp/ports.ts
src/commerce/mcp/service.ts
src/commerce/preview/service.ts
src/commerce/preview/types.ts
src/commerce/publication/lifecycle.ts
src/commerce/publication/ports.ts
src/commerce/publication/validation.ts
src/studio/contracts.ts
src/studio/preview/preview-screen.tsx
src/studio/testing/in-memory-studio-services.ts
tests/backend-postgres-rehearsal.test.ts
tests/c20-integration-fixture.test.ts
tests/commerce-lifecycle.test.ts
tests/definition-execution-mcp.test.ts
tests/external-preview.test.ts
tests/external-wiring.test.ts
tests/fixtures/publication-store.ts
tests/local-external-mcp-diagnostic.test.ts
tests/mcp-authorization.test.ts
tests/mcp-compatibility.test.ts
tests/mcp-service.test.ts
tests/preview-client.test.ts
tests/preview-integration.test.ts
tests/preview-redis-lua.test.ts
tests/preview-routes.test.ts
tests/preview-screen.test.tsx
tests/preview-service.test.ts
tests/preview-store.test.ts
tests/studio-integration-c20.test.ts
tests/studio-integration.test.ts
tests/studio-services.test.ts
tests/studio-workspace.test.tsx
```

The final implementation history includes primary implementation commit `7a32569`, focused C20 correction commit `802930a`, and final normal `origin/main` merge `1a325609cb08ba00324ace611121bc5b3104d272`.

### Work Completed

Moved release composition to direct Capability membership, pinned each member to its Tool's latest published revision, and snapshot Feature behaviour once per represented Feature. Runtime manifest generation now reads immutable release rows, retains Feature eligibility as a separate concern, supports zero eligible capabilities, and deduplicates shared Tool grants. Updated release activation/inspection, Preview and Studio integration surfaces and focused regression fixtures. The C20 fixture now uses C088 Feature authoring APIs and direct Capability grants.

### Validation Results

On final merged implementation branch `task/ARCH-021-COMMERCE-089`:
- Required disposable C20 PostgreSQL/Redis proof: PASS, 2/2 tests; task-owned containers and network cleaned up.
- Focused post-merge matrix: 149 passed; 2 failed in `backend-integration.test.ts` because two existing process-global backend tests expected `getCommerceBackend()` to throw but received `undefined`.
- Focused backend subset: 6 passed, 2 skipped (the two failing process-global cases).
- Studio release service suite and focused lifecycle, MCP, Preview, response processing, Preview Screen and external Preview suites passed.
- C20 Studio integration suite was also exercised: 3 passed, 2 failed. Rollback is rejected by the database's `ARCH020 empty release` guard; a later Tool publication assertion returns unavailable. This adjacent legacy integration path is not the required C20 fixture proof.
- Targeted ESLint: 0 errors, 3 warnings. Changed-file Pylance diagnostics: no errors.
- Full repository TypeScript check: 38 errors in 12 files, none in the C089-owned/modified files. Errors are in unrelated Commerce Studio tooling/tests and the newly merged Capability authoring screen tests.
- Bounded legacy-token search in the C20 fixture, C20 fixture test and Preview adapters: no matches. `git diff --check`: PASS.

### Deviations

Two small post-merge test corrections were committed after the initial implementation commit: align the C20 grant rejection expectation with the current ARCH021 database trigger message, and remove a stale C20 fixture revisionId reference from the ADMIN authorization test. Latest `origin/main` was merged normally after it advanced during validation.

### Assumptions

Repository-wide TypeScript and adjacent backend test failures are recorded as unrelated to this task because none are in the C089-owned/modified files or release composition behavior. The required direct C20 fixture proof passed on the final merged branch.

Execution evidence was reconciled before Architect acceptance:

- canonical parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-089`;
- canonical Commerce implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-089`;
- durable launcher claim commit `8d6f35690f33a6ca1e973c048a279167110f22bd` records Attempt 1, executor `copilot`, claimed at `2026-09-29T14:29:05Z`;
- final Commerce implementation HEAD and remote task ref matched at `1a325609cb08ba00324ace611121bc5b3104d272`;
- final Commerce history contains the normal `origin/main` merge at `1a325609...`, after which the final validation packet was run;
- recursive submodule status resolved database at `e9fb60221f1532205650154dfff2aadb6270b14c`;
- after final parent synchronization with current `origin/main`, parent HEAD and remote task ref matched at pre-acceptance commit `b9f7ef9b0d02e93a115fa7b10189a9def4535cc0`.

The implementation worktree contained unrelated untracked local artifacts (`.DS_Store` and a terminal capture file named `typescript`); neither is part of the committed C089 source delta or remote task branch.

### Unresolved Issues

Repository-wide typecheck remains non-green (38 diagnostics in 12 files). Two process-global backend integration tests and two tests in the adjacent C20 Studio integration suite remain failing as detailed above; they were not expanded into this task's scope.

### Architectural Concerns

None identified. Background consumer changes and COMMERCE-092 legacy deletion were not started.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted ARCH-021-COMMERCE-089 Attempt 1. The implementation replaces Capability-revision release composition with direct Capability membership, deterministically pins the exact published Tool revision at release creation, snapshots Feature behaviour once per represented Feature and builds runtime manifests from immutable release rows. The C20 and Preview corrections remove the remaining C089-path BASE/`conversation_core` assumptions without expanding into COMMERCE-092 cleanup.

The original launcher terminal packet was not retained, but the required execution evidence is durably reconstructed from the launcher claim commit, canonical dedicated worktrees, remote-aligned final task refs, final normal `origin/main` merge and post-merge validation. No source-code rework or test rerun is required for this report-only reconciliation.

### Reviewed Files

The complete final implementation delta is recorded in the Completion Report. Architect review focused on:

- `src/commerce/publication/lifecycle.ts`
- `src/commerce/publication/ports.ts`
- `src/commerce/publication/validation.ts`
- `src/commerce/integration/backend.ts`
- `src/commerce/integration/backend/publication-storage.ts`
- `src/commerce/integration/backend/c20-test-fixture.ts`
- `src/commerce/integration/studio/services.ts`
- `src/commerce/mcp/authorization.ts`
- `src/commerce/mcp/service.ts`
- `src/commerce/integration/preview/adapters.ts`
- `tests/c20-integration-fixture.test.ts`
- focused lifecycle/backend/MCP/Preview/Studio regression fixtures and package metadata.

### Validation Reviewed

- Required disposable C20 PostgreSQL/Redis proof: PASS, 2/2; task-owned resources cleaned up.
- Focused post-merge matrix: 149 passed; two process-global backend expectation failures are outside C089 behavior.
- Focused backend subset: 6 passed, 2 skipped for those same process-global cases.
- Studio release, lifecycle, MCP, Preview, response-processing, Preview Screen and external Preview packets passed.
- Targeted ESLint: 0 errors, 3 warnings; changed-file diagnostics contain no C089 errors.
- Repository typecheck remains non-green with 38 diagnostics across 12 non-C089 files; no diagnostic is in the C089-owned/modified set.
- Bounded C089 legacy-token audit and `git diff --check`: PASS.
- Final validation occurred after the normal `origin/main` merge on the final implementation task branch.

### Architecture Conformance

Accepted. C089 conforms to DATABASE-003 and the published Shared 1.0.0 direct Feature/Capability/Tool contract. It does not restore Capability revision IDs, binding discriminators, per-Capability prompts/configuration or Capability-owned result limits. Feature eligibility remains a separate runtime concern expressed through `featureId`, release replay/immutability remains deterministic, and no Background implementation or final repository-wide legacy deletion was started.

### Follow-up

Mark ARCH-021-COMMERCE-089 Complete. ARCH-021-BACKGROUND-002 is now Ready because DATABASE-003, SHARED-002 and COMMERCE-089 are Complete. COMMERCE-092 remains Pending until BACKGROUND-002 is also Complete; its COMMERCE-089 and COMMERCE-091 dependencies are satisfied.
