---
id: ARCH-021-COMMERCE-061
architecture_id: ARCH-021
title: Establish Shopify Admin schema exploration and query-building domain
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 72
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-018
enables:
  - ARCH-021-COMMERCE-064
created: 2026-09-27
updated: 2026-09-27
---

# Establish Shopify Admin schema exploration and query-building domain

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add a non-React Shopify Admin `2026-07` exploration/query-authoring domain over the existing pinned Admin introspection artifact so Studio can browse Admin fields and arguments, build bounded `SHOPIFY_ADMIN_GRAPHQL` read queries, and round-trip representable manually authored Admin GraphQL without depending on Storefront-specific schema/query-builder contracts.

## Context

The current Explore Shopify implementation is built around the pinned Storefront artifact and Storefront-only builder types. New Tool creation, however, creates `SHOPIFY_ADMIN_GRAPHQL` definitions and the accepted Admin compiler already validates Admin `2026-07` queries.

This task creates the backend/pure-domain capability required by the later UI task. It deliberately leaves the existing Storefront Explore UI operational until COMMERCE-064 migrates the screen.

## Scope

Expected implementation areas include:

```text
lib/discovery/admin-2026-07 artifact consumers
lib/discovery/schema.ts or focused Admin discovery modules
lib/discovery/service.ts
src/commerce/integration/studio/services.ts
src/studio/server-actions.ts
src/studio/discovery/                         # non-React query/selection utilities only

tests/admin-graphql-compiler.test.ts
tests/discovery.test.ts
new focused Admin discovery/query-builder tests
```

## Out of Scope

- React/UI changes to Explore Shopify.
- `sessionStorage` or navigation handoff.
- Removing Storefront support.
- Tool runtime provider execution.
- Result-template authoring.
- Admin result-schema derivation; COMMERCE-062 owns it.
- Live Shopify schema introspection per user click.
- Shopify Admin mutations.

## Requirements

### R1 — Admin artifact is the source of truth

Use the retained pinned Shopify Admin `2026-07` introspection artifact and accepted `adminSchemaHash` as the only schema source for this authoring surface.

Normal exploration must not perform live provider introspection.

### R2 — expose an Admin-specific normalized schema graph

Provide a normalized browse contract suitable for UI consumption that includes, as applicable:

```text
apiVersion
schemaHash
root query type
parent type
field name/description
type reference/nullability/list shape
arguments + required/default metadata
deprecation metadata
whether the field is selectable/expandable
restriction reason
pagination/bound information needed by the accepted compiler
```

Do not expose Storefront-specific type names as the canonical Admin contract.

### R3 — query builder produces Admin authoring output, not a Tool replacement

Provide pure query-authoring logic that produces only the Shopify execution portion required by the originating Tool draft, conceptually:

```text
{
  apiVersion,
  schemaHash,
  document,
  operationName,
  variables
}
```

It must not overwrite Tool description, input schema, result path/schema, response template or other unrelated Tool state.

### R4 — generated GraphQL obeys the accepted Admin compiler

Generated documents must conform to COMMERCE-018 rules, including named read query, bounded selection, no fragments/directives, allowed arguments and literal connection bounds.

Every generated candidate must be validatable by the same `createAdminCommerceCompiler`; do not maintain a weaker visual-builder-only grammar.

### R5 — preserve manual GraphQL as first-class

Provide a bounded parser/round-trip helper for an existing manually authored Admin document.

When the document is representable by the visual builder, recover enough selection/binding state to continue editing.

When the document uses a valid Admin construct outside the visual builder's representable subset, return an explicit `not representable` result. Never silently simplify, reorder semantically significant content, or replace the user's document merely to make it fit the builder.

### R6 — variable bindings remain Tool inputs or literals

The builder may create mappings only from:

```text
Tool input property
literal value
```

It must never surface Shopify credentials, shop identity or authorization context as model inputs.

### R7 — coexist with Storefront until UI migration

Add the Admin discovery/query-building path without deleting the existing Storefront path in this task. COMMERCE-064 will switch the product UI; COMMERCE-069 will remove obsolete Storefront code afterwards.

## Work Items

- [x] Normalize the pinned Admin introspection graph for bounded Studio browsing.
- [x] Add Admin schema browse service/action contract without changing existing Storefront UI behavior.
- [x] Add Admin selection-tree/query-generation logic using GraphQL ASTs.
- [x] Add Admin argument-binding generation compatible with Tool input mappings/literals.
- [x] Add representable-manual-query parse/round-trip support.
- [x] Validate generated queries through the canonical Admin compiler in tests.
- [x] Add deterministic not-representable behavior for unsupported manual constructs.

## Interfaces / Contracts

Consumes:

```text
lib/discovery/artifacts/admin-2026-07.json
adminSchemaHash
createAdminCommerceCompiler
Commerce Tool input-schema/mapping rules
```

Produces a Commerce-internal Admin discovery/query-authoring contract for COMMERCE-064.

No Shared package publication is required.

## Dependencies

- `ARCH-021-COMMERCE-018`

## Enables

- `ARCH-021-COMMERCE-064`

## Acceptance Criteria

- [x] Admin browse starts at the real Admin query root.
- [x] Returned schema identity is Admin `2026-07` and the accepted Admin schema hash.
- [x] Nested fields/arguments are derived from the pinned Admin artifact.
- [x] Generated GraphQL validates with the canonical Admin compiler.
- [x] Generated execution output contains only Admin query-authoring fields.
- [x] Tool input/literal argument mappings are preserved deterministically.
- [x] A representable manual Admin query can seed the builder state.
- [x] A valid but non-representable manual query is preserved and reported as non-representable.
- [x] No live provider introspection occurs.
- [x] Existing Storefront Explore code is not removed by this task.

## Validation

- [x] focused Admin discovery tests
- [x] focused Admin query-builder round-trip tests
- [x] canonical Admin compiler conformance tests
- [x] targeted lint
- [x] changed-file TypeScript diagnostics
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin COMMERCE-064.

## Implementation Notes

Keep normalized schema/query-builder contracts execution-environment neutral and independent of React state. UI labels/presentation belong to COMMERCE-064.

## Completion Report

### Status

Review

### Files Changed

Implementation repository: `moda-interact-commerce`.
- `lib/discovery/admin-schema.ts`
- `lib/discovery/admin-compiler.ts`
- `lib/discovery/service.ts`
- `src/commerce/integration/studio/services.ts`
- `src/studio/contracts.ts`
- `src/studio/server-actions.ts`
- `src/studio/server-services.ts`
- `src/studio/testing/in-memory-studio-services.ts`
- `src/studio/discovery/admin-query-builder.ts`
- `tests/admin-discovery.test.ts`
- `tests/admin-query-builder.test.ts`
- `tests/discovery.test.ts`

Implementation commits: `d1f1e76b3c0acbed86275d7f191e82e3edda6b0c` (Attempt 1) and `9063353fe81fbf848b45fc737290a7effb8b352d` (Attempt 2, pushed).
Remote branch: `origin/task/ARCH-021-COMMERCE-061`.

Prepared execution evidence:
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-061`, branch `task/ARCH-021-COMMERCE-061`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-061`, branch `task/ARCH-021-COMMERCE-061`.
- Shared workspace checkout switched/mutated: no. Shared implementation checkout switched/mutated: no. Another task worktree reused: no.
- Attempt 2 parent task remote fast-forward: not needed; parent `origin/main` incorporated: already current.
- Attempt 2 implementation task remote fast-forward: not needed; implementation `origin/main` incorporated: already current.
- Recursive submodule sync and update: passed; `database` at `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Attempt 2 launcher claim: executor `copilot`, claimed at `2026-09-27T14:55:32Z`, parent claim commit `ac23ba69d72470c3965f1124f2bfa48cc7072ab6`, pushed. Parent and implementation worktrees were reused at the exact canonical task paths; both task branches were already current with `origin/main` and their remote task branches.

### Work Completed

Added an Admin-only normalized schema browse contract over the pinned `admin-2026-07.json` artifact and accepted `adminSchemaHash`, including nested type references, argument/default/deprecation metadata, bounded paging/search, selectable/expandable flags and compiler-aligned forward-pagination bounds. Exposed it through `DiscoveryService`, authenticated Studio service/action wiring and the in-memory service while retaining the existing Storefront browse path.

Added pure GraphQL-AST query generation over normalized Admin schema pages. It emits only `apiVersion`, `schemaHash`, `document`, `operationName` and `variables`; enforces the pinned schema identity, selection/depth/cost/document limits, literal `first` bounds and declared Tool-input mappings; and excludes managed shop/auth/credential input names. Added bounded manual-query parsing that seeds representable selection/binding state and returns exact source text with an explicit `not-representable` result for aliases or variable defaults the builder cannot preserve.

Attempt 2 extracted the compiler's pinned-schema, document, operation and mapping checks into `compileAdminQueryAuthoring`, shared by both generated-query validation and manual-query parsing. This preserves one canonical argument-compatibility implementation while keeping Response-owned `resultPath` and `resultSchema` checks in full execution compilation only. The builder resolves fields across every loaded page for a parent type and constructs valid nested list/non-null variable types.

Architect Review correction disposition:
1. Implemented in `lib/discovery/admin-compiler.ts`, `src/studio/discovery/admin-query-builder.ts` and `tests/admin-query-builder.test.ts`: generated Tool-input and literal bindings are checked by the canonical Admin authoring validator before an output is returned. Tests reject a number input for a String argument and an object literal for an enum argument; accepted generated query candidates pass canonical mapped-argument validation.
2. Implemented in `src/studio/discovery/admin-query-builder.ts` and `tests/admin-query-builder.test.ts`: selected fields are searched across all loaded pages for their parent type. A cursor-0 plus cursor-100 `QueryRoot` regression builds `deliveryProfiles` from the later page and validates it with the canonical compiler.
3. Implemented in `lib/discovery/admin-compiler.ts`, `src/studio/discovery/admin-query-builder.ts` and `tests/admin-query-builder.test.ts`: manual-query parsing uses request-only canonical validation, so a representable valid query is recovered with stale `resultPath`/`resultSchema`; a query violating Admin compiler pagination rules still returns `invalid`.

### Validation Results

Passed:
- `vitest run tests/admin-discovery.test.ts tests/admin-query-builder.test.ts tests/discovery.test.ts tests/admin-graphql-compiler.test.ts tests/discovery-route.test.ts`: 56 tests passed.
- `npm run test:arch021-shopify-admin-compiler`: 22 tests passed.
- Targeted ESLint on `lib/discovery/admin-compiler.ts`, `src/studio/discovery/admin-query-builder.ts` and `tests/admin-query-builder.test.ts`: passed without warnings.
- Changed-file editor diagnostics: no errors in all three Attempt 2 TypeScript files.
- `git diff --check`: passed.

Full `tsc --noEmit` remains blocked by existing repository errors unrelated to this task's Admin-domain changes: missing code-response preview imports, Storefront compiler output-schema typing, the existing Admin oracle fixture typing, the existing `createCommerceStudioServices` missing `createToolWithInitialDraft` implementation, and unrelated test typing errors. The new Admin schema and query-builder files report no compiler/editor diagnostics, and editor diagnostics are clear across all changed files. The remote Shopify Dev MCP oracle was not run; it contacts an external service and is not required by this task's Validation section.

### Deviations

All three corrections requested by Architect Review were implemented within the task scope. No live introspection or Shopify mutations were performed.

### Assumptions

COMMERCE-064 will consume the new Admin-specific browse and pure query-builder contracts. The canonical Admin compiler remains the authority for query validity; result-path and result-schema editing remain outside this task.

### Unresolved Issues

Repository-wide TypeScript validation remains red on the pre-existing errors listed under Validation Results. No task-owned Admin-domain error remains.

### Architectural Concerns

None identified. Storefront exploration remains available and was not migrated or removed.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 is accepted.

The implementation satisfies all three Attempt 1 correction items and the full COMMERCE-061 Admin exploration/query-authoring contract:

1. Generated Tool-input and literal argument bindings are now checked through the canonical Admin query-authoring compiler boundary before a candidate is returned. The builder therefore cannot return a candidate whose mappings fail the same Admin compatibility rules used by execution compilation.
2. Field resolution composes every loaded schema page for the requested parent type rather than only the first page. The cursor-0/cursor-100 `QueryRoot` regression proves a field available only on the later loaded page can be selected and compiled successfully.
3. Manual-query parsing now uses a canonical Request-owned Admin authoring validator that checks pinned schema identity, document/operation semantics and variable mappings without requiring Response-owned `resultPath`/`resultSchema` validity. Invalid Admin query/compiler rules, including unbounded pagination, continue to return `invalid`.

The small `typeNode(...)` correction also preserves valid GraphQL list element nullability such as `[Type!]` while continuing to reject an invalid nested non-null wrapper. This remains within the query-authoring contract.

The broader C061 architecture remains conformant: the pinned Admin `2026-07` artifact is the source of truth; discovery/query-building are pure non-React Commerce-domain capabilities; no live Shopify introspection or mutation is introduced; generated output is limited to Admin Request/execution authoring fields; manual GraphQL remains first-class; managed shop/auth values are excluded from Tool inputs; and the Storefront path remains intact for COMMERCE-064 migration.

COMMERCE-039 is already Complete. With COMMERCE-061 now accepted Complete, both dependencies of COMMERCE-064 are satisfied, so COMMERCE-064 is promoted from Pending to Ready.

### Reviewed Files

- `lib/discovery/admin-compiler.ts`
- `lib/discovery/admin-schema.ts`
- `lib/discovery/service.ts`
- `src/studio/discovery/admin-query-builder.ts`
- `src/studio/contracts.ts`
- `src/studio/server-actions.ts`
- `src/studio/server-services.ts`
- `src/studio/testing/in-memory-studio-services.ts`
- `tests/admin-discovery.test.ts`
- `tests/admin-query-builder.test.ts`
- `tests/discovery.test.ts`
- `tests/admin-graphql-compiler.test.ts`
- `docs/decisions/commerce/ARCH-021/COMMERCE-061-establish-admin-schema-exploration-domain.md`
- `docs/decisions/commerce/ARCH-021/COMMERCE-064-rebuild-explore-shopify-admin-authoring.md`
- `docs/decisions/commerce/ARCH-021/_index.md`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

### Validation Reviewed

Submitted/recorded Attempt 2 validation:

- focused Admin discovery/query/compiler packet: 56/56 passed;
- `npm run test:arch021-shopify-admin-compiler`: 22/22 passed;
- targeted ESLint on Attempt 2 changed files: passed;
- changed-file TypeScript/editor diagnostics: clean;
- `git diff --check`: passed;
- repository-wide TypeScript checking was not rerun for Attempt 2; the previously recorded unrelated repository diagnostics remain outside the task-owned Admin-domain changes.

Source inspection confirms the regressions exercise the three required correction cases and that the extracted authoring validator is reused by the full Admin compiler rather than creating a second compatibility grammar. The submitted archive does not contain installable dependencies, so the test commands were not independently rerun in this review environment; the pushed/clean worktree and validation results are recorded from the Completion Report/submission.

### Architecture Conformance

Conformant.

- Admin `2026-07` pinned schema identity remains authoritative.
- Query-authoring validation and execution compilation share one document/mapping compatibility implementation.
- Request-owned Admin query validity is independent of Response-owned result-contract state.
- Loaded discovery pages compose deterministically for query building.
- No React/UI implementation, provider execution, Storefront removal, result-schema derivation or COMMERCE-064 implementation was added.

### Follow-up

None for COMMERCE-061.

Task is architect-accepted Complete at Attempt 2. ARCH-021-COMMERCE-064 is promoted to Ready because ARCH-021-COMMERCE-039 and ARCH-021-COMMERCE-061 are both Complete.
