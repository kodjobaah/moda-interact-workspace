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
status: in_progress
priority: 72
executor: copilot
claimed_at: 2026-09-27T14:19:17Z
attempt: 1
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

- [ ] Normalize the pinned Admin introspection graph for bounded Studio browsing.
- [ ] Add Admin schema browse service/action contract without changing existing Storefront UI behavior.
- [ ] Add Admin selection-tree/query-generation logic using GraphQL ASTs.
- [ ] Add Admin argument-binding generation compatible with Tool input mappings/literals.
- [ ] Add representable-manual-query parse/round-trip support.
- [ ] Validate generated queries through the canonical Admin compiler in tests.
- [ ] Add deterministic not-representable behavior for unsupported manual constructs.

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

- [ ] Admin browse starts at the real Admin query root.
- [ ] Returned schema identity is Admin `2026-07` and the accepted Admin schema hash.
- [ ] Nested fields/arguments are derived from the pinned Admin artifact.
- [ ] Generated GraphQL validates with the canonical Admin compiler.
- [ ] Generated execution output contains only Admin query-authoring fields.
- [ ] Tool input/literal argument mappings are preserved deterministically.
- [ ] A representable manual Admin query can seed the builder state.
- [ ] A valid but non-representable manual query is preserved and reported as non-representable.
- [ ] No live provider introspection occurs.
- [ ] Existing Storefront Explore code is not removed by this task.

## Validation

- [ ] focused Admin discovery tests
- [ ] focused Admin query-builder round-trip tests
- [ ] canonical Admin compiler conformance tests
- [ ] targeted lint
- [ ] changed-file TypeScript diagnostics
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin COMMERCE-064.

## Implementation Notes

Keep normalized schema/query-builder contracts execution-environment neutral and independent of React state. UI labels/presentation belong to COMMERCE-064.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

None.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending review.

### Follow-up

None.
