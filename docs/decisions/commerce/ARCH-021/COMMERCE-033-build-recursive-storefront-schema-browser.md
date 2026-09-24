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
status: complete
priority: 25
executor: null
claimed_at: null
attempt: 3
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

- [x] Add pure nested selection-tree helpers.
- [x] Extract/add recursive Storefront schema-browser UI.
- [x] Start from the artifact-provided root type.
- [x] Add lazy child-type browsing/cache.
- [x] Add independent scalar/enum selection behavior.
- [x] Add explicit unsupported/restricted-field presentation.
- [x] Add depth/selection bounds.
- [x] Display real field-argument metadata.
- [x] Reset state on schema identity change.
- [x] Replace old flat `field.path` checklist.
- [x] Add real-contract UI regressions.

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

- [x] No production Storefront schema checkbox identity depends on `field.path`.
- [x] Browser starts from the real schema query root.
- [x] Nested output fields are discovered recursively from actual return types.
- [x] Selecting one leaf never selects unrelated siblings.
- [x] Object ancestors are represented by tree structure, not duplicated checkbox state.
- [x] Restricted fields remain impossible to select.
- [x] Unsupported interface/union traversal fails visibly rather than fabricating a query.
- [x] Depth/selection bounds are visible before Tool validation.
- [x] Tests use the same normalized schema contract production uses.

## Validation

- [x] `npx vitest run tests/storefront-schema-browser.test.tsx tests/studio-workspace.test.tsx tests/discovery.test.ts --reporter=verbose`
- [x] targeted ESLint for every changed source/test file
- [x] `npm run typecheck` (unchanged unrelated baseline may be recorded; zero task-owned diagnostics required)
- [x] source audit:
  ```text
  rg -n "field\.path|selected\.includes\(field\.path\)" components src/studio
  ```
  expected: no Storefront schema-builder matches
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return to `moda_architect` and STOP.

Do not start COMMERCE-034.

## Implementation Notes

The browser is data-driven from the actual pinned schema. Do not special-case `product`, `collection`, `MoneyV2` or another Shopify field/type in production UI logic merely to satisfy tests.

A path string may be produced for display/accessibility, but it must always be derived from the current selection-tree ancestry.

Keep the existing documentation-search tab behavior intact unless a directly required contract update makes a mechanical change necessary.

## Completion Report

### Status

Ready for Review

### Correction Checklist

- [x] Preserved the Attempt 2 production correction: actual ancestry depth parity, terminal depth 8, depth-9 expansion blocked, and 100-node validation counting every `SelectionNode` including ancestors.
- [x] Added a genuinely nested pure `selectedFieldCount()` regression proving root, child, and two sibling leaves count as four nodes.
- [x] Added real-contract browser regressions for the exact 99-to-100 acceptance and 100-to-101 rejection boundary, including unchanged selection, unchecked leaf, and exact bounded status.
- [x] Added schema identity reset coverage for both `schemaHash` and `apiVersion`, including selection clearing, collapsed expansion, and reset status.
- [x] Preserved the restored architect-authored contract, required three-file validation and `tests/discovery.test.ts` coverage without editing this Architect Review.

### Files Changed

Attempt 3 changes are limited to `tests/storefront-schema-browser.test.tsx` in implementation commit `3453240` on `task/ARCH-021-COMMERCE-033`. The Attempt 2 production implementation remains unchanged in this attempt:

- `src/studio/discovery/selection-tree.ts`
- `src/studio/discovery/storefront-schema-browser.tsx`

No unrelated source files, database schema/migrations or submodule gitlinks were changed.

### Work Completed

Attempt 3 completed the missing deterministic regression evidence identified by Architect Review. The browser harness now accepts an initial `SelectionTree` for boundary setup and exposes its recursive selected-node count for assertions. The tests use the real named `browseShopifySchema` action mock and real C032 `browseSchema()` pages for the interacted field, while the boundary setup uses structurally valid selection nodes. The reset regression covers both schema identity dimensions without passing the synthetic API version through `browseSchema()`.

### Validation Results

- Required focused validation passed: `npx vitest run tests/storefront-schema-browser.test.tsx tests/studio-workspace.test.tsx tests/discovery.test.ts --reporter=verbose` — 3 files, 46 tests passed.
- Targeted ESLint passed for `tests/storefront-schema-browser.test.tsx`, `src/studio/discovery/selection-tree.ts` and `src/studio/discovery/storefront-schema-browser.tsx` with zero errors and warnings.
- `npm run typecheck` reached `tsc` but reproduced the unchanged documented baseline: 15 diagnostics across 7 unrelated files. No Attempt 3-owned file appears in the diagnostics.
- Source audit `rg -n "field\.path|selected\.includes\(field\.path\)" components src/studio` returned no Storefront schema-builder matches.
- `git diff --check` passed.

### Git / VCS Evidence

- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-033`, branch `task/ARCH-021-COMMERCE-033`; launcher claim commit `b290710028ba1119b73b9e898c547e83389f2ada`, parent head after claim `56aaa03ba6bfa8713a1a41bc19a75657df56dac1`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-033`, branch `task/ARCH-021-COMMERCE-033`; implementation head before Attempt 3 `5bfbaaf68354e9db27194a20625245e1940a18ce`; published Attempt 3 commit `3453240`.
- Both repositories use the launcher-provided physical worktrees and same task branch. Prepared synchronization and dependency gating were completed by the launcher; dependency `ARCH-021-COMMERCE-032` was complete.
- Database submodule is synchronized at `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Parent publication scope is only this task report. No implementation submodule gitlink is staged.

### Deviations

The repository-wide typecheck remains non-zero only because of the unchanged documented baseline: 15 diagnostics across 7 unrelated files. No implementation deviation was introduced.

### Assumptions

The launcher-provided implementation branch and database submodule are authoritative. The Attempt 2 implementation commit is `5bfbaaf68354e9db27194a20625245e1940a18ce`; Attempt 3 adds only the published test evidence commit `3453240`.

### Unresolved Issues

Repository-wide typecheck must be repaired by the owning follow-up work before it can be reported green. This unchanged baseline does not block the focused Commerce-033 behavior checks; no task-owned diagnostics remain.

### Architectural Concerns

None identified for this bounded task.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 3 completes the deterministic regression evidence requested after Attempt 2.

No production-code redesign was required. Review of the supplied snapshot confirms that Attempt 3 changes the focused browser regression harness/tests while preserving the accepted Attempt 2 production implementation.

The final accepted production behavior remains:

```text
real C032 root/type metadata
  -> named browseShopifySchema Server Action
  -> lazy child-type pages cached by schema identity + parent type
  -> nested SelectionTree
  -> depth bound = 8 total field segments
  -> selected-field bound = 100 total SelectionNode values
```

The final source still enforces:

```ts
if (ancestry.length >= MAX_DEPTH) {
  onStatus(`Selection depth is limited to ${MAX_DEPTH} fields.`);
  return;
}
```

for object expansion, and:

```ts
const candidate = selectLeaf(selection, ancestry);

if (selectedFieldCount(candidate) > MAX_SELECTED_FIELDS) {
  onStatus(`Selection is limited to ${MAX_SELECTED_FIELDS} fields.`);
  return;
}
```

for leaf selection.

`selectedFieldCount()` recursively counts every selected object ancestor and leaf:

```ts
return tree.reduce(
  (count, node) => count + 1 + selectedFieldCount(node.children),
  0,
);
```

#### Attempt 3 regression evidence accepted

The architect inspected the final `tests/storefront-schema-browser.test.tsx` and confirmed it now proves the missing cases.

1. **Recursive ancestor counting**

A genuinely nested tree:

```text
root
  child
    leafA
    leafB
```

is asserted to contain exactly four selected fields.

This proves the helper counts object ancestors and leaves rather than only independent roots/leaves.

2. **Exact 100/101 browser boundary**

The test harness now supports test-only initial `SelectionTree` state without adding any production test seam to `StorefrontSchemaBrowser`.

The accepted regression exercises a real C032-backed field through the production named Server Action path:

```text
99-node initial tree
  + real product.title selection
  -> 100
  -> checkbox checked

100-node initial tree
  + same real product.title selection
  -> candidate 101
  -> selection remains at 100
  -> checkbox remains unchecked
  -> exact status:
     "Selection is limited to 100 fields."
```

That exercises the browser guard itself rather than merely testing helper arithmetic.

3. **Both schema identity dimensions**

The final regression is parameterized across:

```text
schemaHash change
apiVersion change
```

and proves for each:

```text
selection clears
product branch is collapsed again
status receives:
  "Schema changed; cached fields and validation were reset."
```

The synthetic alternate API version exists only in the React identity-reset test and is not passed through `browseSchema()` or represented as a supported pinned Shopify schema.

4. **Production test-boundary parity**

The browser test continues to mock the same named:

```text
browseShopifySchema
```

module export that production imports.

The interacted field/page data comes from the real C032 `browseSchema()` contract.

No production test-only service/port/fixture prop was introduced.

5. **Source audit**

Architect static inspection of the supplied snapshot found no:

```text
field.path
selected.includes(field.path)
```

usage under the Storefront schema-builder production paths.

#### Submitted validation

The Completion Report records:

```text
focused tests: 3 files / 46 passed
targeted ESLint: PASS
source audit: PASS
git diff --check: PASS
typecheck: 15 unchanged unrelated baseline diagnostics
           zero task-owned diagnostics
```

The review archive does not contain `node_modules`, so the architect did not independently rerun Vitest, ESLint or TypeScript. The final test source itself was inspected against the requested regression contract.

Implementation/test commit reviewed:

```text
3453240d
```

Final parent report supplied:

```text
a54b41e5
```

### Reviewed Files

- `src/studio/discovery/selection-tree.ts`
- `src/studio/discovery/storefront-schema-browser.tsx`
- `tests/storefront-schema-browser.test.tsx`
- `tests/studio-workspace.test.tsx`
- `tests/discovery.test.ts`
- task Completion Report
- Commerce ARCH-021 index/frontier
- parent ARCH-021 execution table/frontier
- COMMERCE-034 dependency gate

### Validation Reviewed

Architect source comparison between the supplied Attempt 2 and Attempt 3 snapshots confirms the production C033 source is unchanged in Attempt 3; the material focused change is the regression test harness/evidence.

Architect independently confirmed the final static source audit contains no Storefront schema-builder `field.path` dependency.

Submitted validation:

```text
3 focused files / 46 tests passed
targeted ESLint passed
source audit passed
git diff --check passed
typecheck retained only the documented 15-error unrelated baseline
```

### Architecture Conformance

Conforms.

The recursive browser is now data-driven from the truthful C032 schema graph, keeps ancestry in client selection state, enforces the same obvious depth/field bounds before later Tool compilation, and has deterministic regression evidence for the previously missing boundary cases.

### Follow-up

`ARCH-021-COMMERCE-033` is Complete.

`ARCH-021-COMMERCE-034` becomes Ready.

`ARCH-021-COMMERCE-035` remains Pending on COMMERCE-034.

Terminal `ARCH-021-SYSTEM-TEST-001` remains Pending until the remaining correction tasks are architect-accepted Complete.

Do not start COMMERCE-035 until COMMERCE-034 is architect-accepted Complete.
