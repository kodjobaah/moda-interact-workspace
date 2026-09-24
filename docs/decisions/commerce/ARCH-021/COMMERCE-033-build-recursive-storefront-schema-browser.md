---
id: ARCH-021-COMMERCE-033
architecture_id: ARCH-021
title: Build recursive Storefront schema navigation and selection
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 25
executor: copilot
claimed_at: 2026-09-24T21:42:23Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-032
enables:
  - ARCH-021-COMMERCE-034
created: 2026-09-24
updated: 2026-09-24
---

# Build recursive Storefront schema navigation and selection

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Replace the flat Storefront field checklist with a recursive schema-driven browser whose authoritative selection state is a tree derived from actual parent/child traversal, so each field has independent identity without server-supplied synthetic paths.

## Context

COMMERCE-032 makes the real pinned Storefront introspection artifact and normalized type graph authoritative.

The current Explore UI stores:

```text
selected: string[]
```

and keys/checks rows with:

```text
field.path
```

even though `path` is not part of Shopify introspection.

The correct source of a nested selection such as:

```text
product.priceRange.minVariantPrice.amount
```

is the actual traversal:

```text
QueryRoot.product -> Product
Product.priceRange -> ProductPriceRange
ProductPriceRange.minVariantPrice -> MoneyV2
MoneyV2.amount -> Decimal
```

This task implements that recursive navigation/selection model. It does not yet generate the final GraphQL document or persist argument bindings into the Tool definition; that is COMMERCE-034.

## Scope

Primary files:

```text
src/studio/discovery/selection-tree.ts             # new pure selection state
src/studio/discovery/storefront-schema-browser.tsx # new UI module
components/studio-workspace.tsx                    # compose new browser
src/studio/server-actions.ts                       # consume COMMERCE-032 browse contract only if required
tests/storefront-schema-browser.test.tsx            # new
tests/studio-workspace.test.tsx
tests/discovery.test.ts
package.json
```

Additional directly affected Studio discovery files may be changed only when required by the new normalized contract.

## Out of Scope

- GraphQL AST/document generation.
- Persisting generated query changes back to the Tool.
- Final argument-to-inputSchema variable mapping.
- Live Shopify schema requests.
- Shopify Admin GraphQL.
- Database/Shared/Background changes.
- New editor framework.
- Hard-coded Shopify field-name UI branches.
- Fragment/interface/union query generation.

## Requirements

### R1 — one production browse path

The browser must use the existing named Studio Server Action:

```text
browseShopifySchema
```

with the COMMERCE-032 normalized response.

Do not add a second schema port/service bundle/test-only production prop.

Tests must mock the same named Server Action boundary used by production.

### R2 — start from the actual query root

The initial browser root is:

```text
schema.rootTypeName
```

from COMMERCE-032.

Do not hard-code `QueryRoot` in the React UI.

### R3 — lazy recursive type navigation

For an expandable field:

1. unwrap its real named output type from the normalized field metadata;
2. request/browse that named type through the same server action;
3. render its child fields;
4. cache the returned type page by:
   ```text
   apiVersion + schemaHash + parentTypeName
   ```
   for the mounted browser session;
5. repeated expand/collapse of the same type must not require a second server call unless the schema identity changes.

Do not preload the full 1.7MB schema artifact into the browser.

### R4 — authoritative selection tree

Create one pure selection-state module.

The authoritative state must be a nested tree, not a flat `string[]` of server-provided paths.

Each selected node must retain enough schema identity to prove where it came from, at least:

```text
parentTypeName
fieldName
namedTypeName
namedTypeKind
children
```

It may also retain schema argument metadata required by COMMERCE-034.

A display path may be derived recursively for labels/ARIA/debug output, for example:

```text
product.priceRange.minVariantPrice.amount
```

but that derived string is not the source of truth.

### R5 — scalar/enum leaf selection

Leaf output fields that the normalized graph marks selectable may be independently selected/unselected.

Selecting:

```text
product.priceRange.minVariantPrice.amount
```

must not select:

```text
product.title
product.handle
product.priceRange.maxVariantPrice.amount
```

A selected descendant implicitly requires its object ancestors in the selection tree.

Object/list-object ancestors do not need independent checkbox state.

### R6 — expandable-kind policy

For this checkpoint:

```text
OBJECT -> expandable
SCALAR -> selectable leaf
ENUM   -> selectable leaf
```

For output kinds requiring fragments or compiler behavior not currently supported:

```text
INTERFACE
UNION
```

render them explicitly non-selectable/non-expandable with a bounded reason.

Do not introduce fragment generation in this task.

List/non-null wrappers use the named output kind after unwrapping.

### R7 — restriction visibility

If COMMERCE-032 says:

```text
selectable: false
restrictionReason: ...
```

the UI must:

- disable selection;
- display the bounded reason;
- never add that field to the selection tree.

No client-side duplicate authorization/restriction matrix may override the server result.

### R8 — bounded recursive navigation

Preserve accepted Storefront compiler bounds in the authoring UI:

```text
maximum field-selection depth: 8
maximum selected fields:       100
```

The browser must prevent further selection/expansion when the corresponding bound would be exceeded and show a bounded user-visible reason.

Do not rely on the later compiler to be the first place those obvious bounds become visible.

### R9 — argument metadata is displayed, not fabricated

Fields with arguments must display their actual normalized argument names/types/required state.

COMMERCE-033 may retain draft placeholders for later argument binding, but it must not invent values or silently satisfy required arguments.

A field requiring unresolved arguments may still be browsed so the user can inspect descendants, but the browser must expose that argument configuration is still required before the selection can become a valid Tool query.

COMMERCE-034 owns final argument-binding controls and query compilation.

### R10 — schema identity changes reset incompatible browser state

If either:

```text
apiVersion
schemaHash
```

changes while the browser is mounted, clear:

```text
expanded-type cache
selection tree
validation state
```

Do not carry selection identities across schema artifacts.

### R11 — fixture parity

React tests must derive schema pages by calling the real COMMERCE-032 `browseSchema()` contract behind the mocked named Server Action.

Do not hand-author richer field fixtures containing properties production does not return.

## Work Items

- [ ] Add pure nested selection-tree helpers.
- [ ] Extract/add recursive Storefront schema-browser UI.
- [ ] Start from the artifact-provided root type.
- [ ] Add lazy child-type browsing/cache.
- [ ] Add independent scalar/enum selection behavior.
- [ ] Add explicit unsupported/restricted-field presentation.
- [ ] Add depth/selection bounds.
- [ ] Display real field-argument metadata.
- [ ] Reset state on schema identity change.
- [ ] Replace old flat `field.path` checklist.
- [ ] Add real-contract UI regressions.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-032 normalized Storefront discovery contract
```

Produces one Commerce-local Storefront selection-tree representation consumed by:

```text
ARCH-021-COMMERCE-034
```

No cross-service contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-032

## Enables

- ARCH-021-COMMERCE-034

## Acceptance Criteria

- [ ] No production Storefront schema checkbox identity depends on `field.path`.
- [ ] Browser starts from the real schema query root.
- [ ] Nested output fields are discovered recursively from actual return types.
- [ ] Selecting one leaf never selects unrelated siblings.
- [ ] Object ancestors are represented by tree structure, not duplicated checkbox state.
- [ ] Restricted fields remain impossible to select.
- [ ] Unsupported interface/union traversal fails visibly rather than fabricating a query.
- [ ] Depth/selection bounds are visible before Tool validation.
- [ ] Tests use the same normalized schema contract production uses.

## Validation

- [ ] `npx vitest run tests/storefront-schema-browser.test.tsx tests/studio-workspace.test.tsx tests/discovery.test.ts --reporter=verbose`
- [ ] targeted ESLint for every changed source/test file
- [ ] `npm run typecheck` (unchanged unrelated baseline may be recorded; zero task-owned diagnostics required)
- [ ] source audit:
  ```text
  rg -n "field\.path|selected\.includes\(field\.path\)" components src/studio
  ```
  expected: no Storefront schema-builder matches
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return to `moda_architect` and STOP.

Do not start COMMERCE-034.

## Implementation Notes

The browser is data-driven from the actual pinned schema. Do not special-case `product`, `collection`, `MoneyV2` or another Shopify field/type in production UI logic merely to satisfy tests.

A path string may be produced for display/accessibility, but it must always be derived from the current selection-tree ancestry.

Keep the existing documentation-search tab behavior intact unless a directly required contract update makes a mechanical change necessary.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

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
