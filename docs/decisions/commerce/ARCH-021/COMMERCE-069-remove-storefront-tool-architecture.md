---
id: ARCH-021-COMMERCE-069
architecture_id: ARCH-021
title: Remove obsolete Storefront Tool architecture
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 76
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-060
  - ARCH-021-COMMERCE-064
enables: []
created: 2026-09-27
updated: 2026-09-27
---

# Remove obsolete Storefront Tool architecture

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Complete the pre-production Shopify simplification by removing `SHOPIFY_STOREFRONT_QUERY` as a Moda Commerce Tool execution/authoring mode and deleting the Storefront-only compiler, transport, discovery/query-builder artifacts and tests that are no longer required after Admin execution and Admin Explore authoring are operational.

## Context

The platform is still in development and the user has explicitly approved breaking removal of the transitional Storefront Tool model rather than maintaining compatibility.

By this task:

```text
COMMERCE-060 -> Admin Tool runtime exists
COMMERCE-064 -> Explore Shopify uses Admin API and local authoring sessions
```

There is therefore no product reason to keep a parallel Storefront Tool execution kind.

This task removes the Moda Tool architecture, not legitimate Shopify concepts or schema fields that happen to contain the word `Storefront`.

## Scope

Expected implementation areas include:

```text
src/commerce/tool-definition/contracts.ts
src/commerce/execution/
src/commerce/query/                              # remove Storefront-only runtime
src/commerce/integration/backend/executors.ts
lib/discovery/compiler.ts                        # Storefront Tool compiler
lib/discovery/storefront-artifact.ts
lib/discovery/artifacts/storefront-2026-07.json  # if no remaining legitimate consumer
src/studio/discovery/storefront-*.ts(x)
legacy Storefront fixtures/seeds/tests
architecture-local validation scripts that exist only for Storefront Tool authoring
```

Exact removal must be evidence-driven: retain any file still required for a separate non-Tool capability and report it.

## Out of Scope

- Removing unrelated Shopify Storefront terminology/data from the repository.
- Migrating old development Storefront Tool definitions to Admin GraphQL.
- Building backwards-compatibility adapters.
- Result Template UI.
- General tab traversal/gating.
- Database migrations solely to preserve obsolete development Tool definitions.

## Requirements

### R1 — canonical execution union is Admin-only for Shopify

Remove `SHOPIFY_STOREFRONT_QUERY` from the Commerce Tool execution union and all mapping/type helpers that exist only to support that execution kind.

The Shopify Tool execution kind remaining in new canonical definitions is:

```text
SHOPIFY_ADMIN_GRAPHQL
```

alongside non-Shopify kinds such as External HTTP and policy operations.

### R2 — remove Storefront Tool runtime

Delete the Storefront query execution port/transport/compiler/runtime path and update executable-registry logic to use the Admin path from COMMERCE-060.

Do not leave dead production branches that can still execute a Storefront Tool definition.

### R3 — remove Storefront authoring/discovery implementation replaced by Admin

Delete Storefront-specific Explore schema browser/query builder/argument-binding modules and server discovery branches only after proving COMMERCE-064 no longer imports them.

The `/explore` product surface remains; it is Admin-backed.

### R4 — pre-production data strategy is reset/reseed, not conversion

Do not build automatic Storefront->Admin query conversion. Existing development definitions using the removed kind may be deleted/reseeded according to the existing development workflow.

If test fixtures/seeds contain Storefront definitions, replace them with truthful Admin or non-Shopify equivalents as appropriate.

### R5 — preserve legitimate Shopify concepts

Do not mechanically remove every identifier/string containing `storefront`. Shopify Admin schema fields, external documentation wording, or unrelated storefront concepts remain when they serve a real capability.

Removal decisions must be tied specifically to the obsolete Moda Tool execution/Explore implementation.

### R6 — final publication/runtime no longer accepts Storefront Tool definitions

Canonical parsing/publication/execution tests must prove a `SHOPIFY_STOREFRONT_QUERY` definition is no longer accepted as a Commerce Tool definition.

No compatibility parser is retained.

## Work Items

- [x] Remove Storefront execution kind from canonical Tool contracts.
- [x] Remove Storefront execution port/transport/runtime and availability branches.
- [x] Remove Storefront Tool compiler/publication-specific code.
- [x] Remove obsolete Storefront Explore/query-builder modules after import verification.
- [x] Remove obsolete Storefront schema artifact/provenance only if no legitimate consumer remains.
- [x] Replace/remove Storefront Tool fixtures, seeds and tests.
- [x] Add negative canonical-contract test proving removed kind is rejected.
- [x] Verify Admin runtime/Explore/Request/Response regressions remain green.

## Interfaces / Contracts

Removes the repository-local `SHOPIFY_STOREFRONT_QUERY` Tool execution contract.

No replacement cross-service contract is introduced; `SHOPIFY_ADMIN_GRAPHQL` is already canonical.

## Dependencies

- `ARCH-021-COMMERCE-060`
- `ARCH-021-COMMERCE-064`

## Enables

None.

## Acceptance Criteria

- [x] `SHOPIFY_STOREFRONT_QUERY` is absent from the canonical Commerce Tool execution union.
- [x] Production DefinitionExecutor has no Storefront Tool branch.
- [x] Executable-registry availability no longer recognizes Storefront Tool definitions.
- [x] Explore Shopify is Admin-backed and has no Storefront mode.
- [x] Storefront Tool builder/browser modules are removed when no longer imported.
- [x] Obsolete Storefront Tool fixtures/tests are removed or replaced.
- [x] A Storefront Tool definition fails canonical parsing/publication.
- [x] Admin Tool runtime and Admin Explore authoring remain green.
- [x] No backwards-compatibility adapter or migration is introduced.
- [x] Legitimate unrelated Shopify Storefront concepts are not removed mechanically.

## Validation

- [x] canonical Tool contract tests
- [x] Admin execution tests
- [x] Admin Explore/query-builder tests
- [x] Shopify authoring UI tests
- [x] repository search proving no remaining production `SHOPIFY_STOREFRONT_QUERY` branch
- [x] targeted lint
- [x] changed-file TypeScript diagnostics (C069-linked diagnostics were resolved; workspace-wide typecheck still reports unrelated existing diagnostics documented below)
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin later traversal/coordination work.

## Implementation Notes

Because this is a pre-production breaking simplification, prefer deletion over compatibility shims. If a Storefront artifact remains for a legitimate separate capability, document that evidence rather than deleting it merely by name.

## Completion Report

### Status

Ready for Architect Review

### Files Changed

Commerce Tool definition/execution, publication, backend composition, Admin discovery, Studio authoring, preview adapters, tests, and documentation were updated. Storefront-only compiler/schema artifacts, query runtime/ports, Explore browser/query builder, artifact checker, and corresponding tests were deleted. Preserved the Admin 2026-07 schema artifact, including legitimate Storefront-named Admin fields.

### Work Completed

Removed the `SHOPIFY_STOREFRONT_QUERY` definition and runtime path without adding conversion or compatibility behavior. Admin GraphQL is now the retained Shopify Tool execution and Explore path; documentation lookup remains available. Removed unreferenced Storefront-only schema and authoring modules after confirming there were no consumers. Updated canonical negative tests, Admin execution and authoring fixtures, preview generation, and documentation. Corrected the Admin editor delayed-save race so edits made while a save is pending remain dirty until the workspace revision guard accepts them. Removed the obsolete query port from the local external MCP diagnostic fixture. Restored the Studio initial-draft service contract while preserving its mutation adapter entry point.

### Validation Results

Passed focused Vitest run: 11 files, 114 tests, including canonical contract rejection, Admin compiler/discovery, Admin execution, preview integration, Studio, MCP, authoring validation, and Admin query-builder coverage. ESLint passed across all changed JavaScript/TypeScript files. `git diff --check` passed. A production/source scan found no remaining Storefront Tool execution/compiler/availability branch; remaining `SHOPIFY_STOREFRONT_QUERY` literals are explicit rejection fixtures, and Admin schema/docs retain legitimate Storefront concepts.

`npx tsc --noEmit` is not clean workspace-wide. Remaining diagnostics are in unrelated or pre-existing areas, including missing preview modules imported by `app/api/studio/code-response/validate/route.ts`, Admin schema/query-builder and readonly schema fixtures, and unrelated test typing. The C069-linked missing publication type import, Studio service contract, obsolete C20 `query` dependency, and local external MCP `query` dependency were resolved. The C20 disposable-database integration test was not run because its isolated PostgreSQL/Redis targets were not configured. An earlier broader test run had two backend singleton assertion failures; the final focused 114-test set passes.

### Deviations

The full C20 integration and a clean workspace-wide typecheck were not attainable in this environment; focused runtime/UI suites and changed-file lint passed. The local external MCP diagnostic was linted but not executed because it requires the disposable database and Redis environment.

### Assumptions

This is a pre-production breaking removal as specified. Existing development Storefront Tool data is reset/reseeded rather than converted. Shopify Storefront concepts that are genuine Admin schema fields or documentation content remain intact.

### Unresolved Issues

Workspace-wide TypeScript diagnostics remain outside this task's changed implementation paths, including unresolved preview imports and readonly test-schema fixtures. The disposable C20 PostgreSQL/Redis integration still needs an environment-backed run.

### Architectural Concerns

None identified. No compatibility adapter, data conversion, or migration was introduced.

### Execution Evidence

- Physical isolation: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-069`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-069`; both branches are `task/ARCH-021-COMMERCE-069`. The shared workspace and implementation source checkouts were not switched or edited for task work; no other task worktree was reused.
- Launcher synchronization: parent remote task branch fast-forward `not-needed`, parent `origin/main` `already-current`; implementation remote task branch fast-forward `not-needed`, implementation `origin/main` `already-current`.
- Recursive implementation submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; recorded database submodule commit `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Parent claim commit `2ed11d907b6e41c0c51e5d25254e62b2c2e1e92f` was already committed and pushed by the launcher. Implementation commit `5bd4b49` was pushed to `origin/task/ARCH-021-COMMERCE-069`.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is accepted. The obsolete `SHOPIFY_STOREFRONT_QUERY` Tool execution/authoring architecture is removed from canonical Commerce definitions, production execution/availability, Storefront-only compiler/query-builder/browser artifacts and their obsolete tests. Shopify Admin GraphQL remains the canonical Shopify Tool path, and the retained Storefront-named Admin schema/documentation content is legitimate non-Tool terminology rather than compatibility drift.

The final unchecked regression Work Item was a task-record inconsistency only: the Completion Report and focused 114-test validation packet already record the Admin runtime/Explore/Request/Response regressions as green. The archived task file also still carried the execution claim despite the reported review handoff; architect acceptance reconciles `executor`/`claimed_at` to null. Neither issue requires implementation churn.

The unavailable disposable C20 PostgreSQL/Redis integration and workspace-wide TypeScript diagnostics are non-blocking for C069 because neither is part of the task's required validation contract, changed-file diagnostics/lint passed, and the focused removal/regression packet is green.

### Reviewed Files

- `src/commerce/tool-definition/contracts.ts`
- `src/commerce/tool-definition/mappings.ts`
- `src/commerce/execution/executor.ts`
- `src/commerce/execution/ports.ts`
- `src/commerce/integration/backend/executors.ts`
- `src/commerce/integration/backend.ts`
- `lib/discovery/service.ts`
- `app/api/studio/discovery/route.ts`
- `components/studio-workspace.tsx`
- `src/studio/discovery/admin-explorer.tsx`
- `src/studio/discovery/admin-query-builder.ts`
- `tests/arch021-commerce-tool-contract.test.ts`
- `tests/commerce-lifecycle.test.ts`
- `tests/shopify-admin-tools-ui.test.tsx`

Also reviewed repository searches confirming no production `SHOPIFY_STOREFRONT_QUERY` branch and no remaining Storefront-only Tool compiler/browser/query-builder module.

### Validation Reviewed

- Focused Vitest packet: 11 files / 114 tests passed.
- Canonical negative tests reject `SHOPIFY_STOREFRONT_QUERY`.
- Admin runtime, Admin Explore/query-builder, preview/Studio and authoring regressions are included in the reported focused green packet.
- Targeted ESLint passed for changed JavaScript/TypeScript files.
- Changed-file TypeScript diagnostics are clean; workspace-wide diagnostics remain outside C069-owned implementation paths.
- `git diff --check` passed.
- Disposable C20 PostgreSQL/Redis integration was not run because the required isolated services were unavailable; this does not block the task's defined acceptance contract.

### Architecture Conformance

Conforms. C069 performs the approved pre-production breaking removal rather than introducing conversion or compatibility shims, preserves the Admin replacement paths from C060/C064, and leaves legitimate Storefront terminology that belongs to Shopify Admin schema/documentation capabilities intact. No database migration or cross-repository contract change is introduced.

### Follow-up

None. C069 enables no downstream task.
