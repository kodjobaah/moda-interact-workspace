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
status: review
priority: 25
executor: null
claimed_at: null
attempt: 2
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

- [x] Correct depth parity: use actual ancestry length, allow terminal fields at depth 8, and block expansion that would expose depth 9.
- [x] Correct selected-field parity: count every `SelectionNode`, including object ancestors, and reject candidate trees over 100 nodes.
- [x] Preserve the restored architect-authored contract, checklists and required `tests/discovery.test.ts` validation without editing this Architect Review.
- [x] Add the required real-contract UI regressions for root/cache, independent selection/pruning, restrictions, unsupported kinds, arguments, depth, total-node bounds and schema identity reset.

### Files Changed

Attempt 2 implementation commit `5bfbaaf` on `task/ARCH-021-COMMERCE-033` in `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-033` changed:

- `src/studio/discovery/selection-tree.ts`
- `src/studio/discovery/storefront-schema-browser.tsx`
- `tests/storefront-schema-browser.test.tsx`

The prior implementation files remain part of the branch at `d8ed6b9d415f393ac50a8a939ff1171759d9201c`; no unrelated source files were changed in Attempt 2.

### Work Completed

Implemented the requested Attempt 2 corrections. `selectedFieldCount()` now counts every selected ancestor and leaf; the browser validates the candidate tree against 100 total fields. Expansion and terminal selection use the actual ancestry length, so depth 8 is the final selectable field depth and depth 9 cannot be exposed. The focused browser tests now exercise the real pinned schema contract, including the compiler-boundary regression cases.

### Validation Results

Required focused validation passed: `npx vitest run tests/storefront-schema-browser.test.tsx tests/studio-workspace.test.tsx tests/discovery.test.ts --reporter=verbose` passed 3 files and 44 tests. Targeted ESLint passed for `src/studio/discovery/selection-tree.ts`, `src/studio/discovery/storefront-schema-browser.tsx` and `tests/storefront-schema-browser.test.tsx`. The source audit `rg -n "field\.path|selected\.includes\(field\.path\)" components src/studio` returned no matches, and `git diff --check` passed. `npm run typecheck` reached `tsc` but remains blocked by the unchanged baseline of 15 errors across 7 unrelated files; no task-owned file is named in those diagnostics.

### Git / VCS Evidence

- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-033`, branch `task/ARCH-021-COMMERCE-033`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-033`, branch `task/ARCH-021-COMMERCE-033`.
- Prepared sync/base evidence: parent sync head `560fa26560e6174684f21a2f17a9813941277ae8`; implementation prior head `d8ed6b9d415f393ac50a8a939ff1171759d9201c`; Attempt 2 claim commit `840a942e0ad2c6a72ba266632bd4a24ed9adf4be`.
- Implementation commit `5bfbaaf` is pushed and matches `origin/task/ARCH-021-COMMERCE-033`.
- Database submodule: `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Publication scope: only this parent task report is to be committed on the parent branch; the implementation branch contains the source/test correction commit above. No submodule gitlink is staged.

### Deviations

The repository-wide typecheck remains non-zero only because of the unchanged documented baseline: 15 diagnostics across 7 unrelated files. No implementation deviation was introduced.

### Assumptions

The implementation branch and database submodule supplied in the handoff are the authoritative inputs: prior implementation `d8ed6b9d415f393ac50a8a939ff1171759d9201c`, Attempt 2 implementation `5bfbaaf`, database submodule `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.

### Unresolved Issues

Repository-wide typecheck must be repaired by the owning follow-up work before it can be reported green. This unchanged baseline does not block the focused Commerce-033 behavior checks; no task-owned diagnostics remain.

### Architectural Concerns

None identified for this bounded task.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 establishes the correct recursive schema-browser architecture in substance:

- the browser starts from the C032-provided schema root rather than a hard-coded `QueryRoot`;
- expandable fields resolve the actual normalized named output type;
- child pages are loaded through the production `browseShopifySchema` named Server Action;
- child pages are cached by API version + schema hash + parent type for the mounted browser session;
- selection state is a nested tree containing parent type, field name, named type/kind, arguments and children;
- scalar/enum leaves use independent selection state;
- restricted fields cannot be selected/expanded;
- interface/union traversal is explicitly unsupported rather than fabricated;
- argument names/types/required state are displayed from the normalized C032 contract;
- schema identity change clears page cache, expansion and selection and triggers the parent validation-stale path;
- no production checkbox identity depends on `field.path`;
- React tests obtain schema pages from the real C032 `browseSchema()` contract behind the same named Server Action production uses.

There are two correctness blockers in the accepted compiler-bound requirements, plus one task-protocol correction.

#### Finding 1 — the browser depth bound is off by one

The accepted Storefront compiler begins traversal at:

```text
root field depth = 1
```

and rejects a nested selection set when the current field depth is already 8. Therefore a selectable leaf may have at most:

```text
8 field segments from the query root
```

The current browser instead calls:

```ts
renderPage(rootPage, [], 0)
```

and allows object expansion while:

```ts
depth < MAX_DEPTH
```

This allows an object whose path already contains 8 field segments to expand and render children containing 9 field segments. Those depth-9 leaves remain selectable because `toggleLeaf()` performs no ancestry-depth check.

That violates R8's requirement to expose the same maximum depth before server Tool validation.

Attempt 2 must use the actual ancestry/path length as the authoritative depth.

Required behavior:

```text
path length 1..7 object -> may expand
path length 8 object    -> must not expand to children
path length <=8 leaf    -> may be selected
path length >8 leaf     -> must never become selectable
```

Do not fix this by changing the compiler bound.

A simple conformant rule is:

```ts
const fieldDepth = nextAncestry.length;

object expansion:
  allow only when fieldDepth < MAX_DEPTH

leaf selection:
  reject when ancestry.length > MAX_DEPTH
```

The displayed reason must remain bounded and identify the maximum of 8.

#### Finding 2 — the 100-field bound counts leaves, but the compiler counts every GraphQL field

The accepted Storefront compiler increments its selected-field count for **every**
GraphQL field in the document:

```text
object ancestors + leaf selections
```

The current browser enforces:

```ts
selectedLeafCount(selection) >= 100
```

which counts only leaves.

Example:

```text
product
  priceRange
    minVariantPrice
      amount
```

is four selected GraphQL fields to the compiler but only one selected leaf to the current browser.

The browser can therefore permit a tree that is already over the compiler's 100-field bound and defer the failure to later Tool validation, contrary to R8.

Attempt 2 must add/use a pure total-node count:

```ts
selectedFieldCount(tree)
```

with semantics:

```text
count every SelectionNode exactly once
```

When selecting a new leaf, compute the candidate tree first:

```ts
const candidate = selectLeaf(selection, ancestry);
```

and reject the selection when:

```ts
selectedFieldCount(candidate) > MAX_SELECTED_FIELDS
```

This correctly accounts for newly introduced object ancestors as well as the leaf.

Do not raise the 100-field compiler bound and do not count only leaves.

`selectedLeafCount()` may remain if COMMERCE-034 genuinely needs leaf count, but it must not implement the R8 total field-selection limit.

#### Finding 3 — the authoritative task definition was narrowed during execution

The submitted task file removed content that was part of the architect-authored execution contract, including:

- the Out of Scope list;
- R7's explicit restricted-field requirements;
- Dependencies and Enables;
- several original Work Items;
- several original Acceptance Criteria;
- `tests/discovery.test.ts` from required focused Validation.

Repository execution may check/reconcile Work Items, Acceptance Criteria and Validation evidence, but it must not silently delete architecture scope, requirements or dependency contracts in order to match the submitted implementation.

This review patch restores the architect-authored task contract and marks only the already-verified items complete.

Attempt 2 must preserve that restored contract. Do not replace the detailed task lists with a shorter summary.

### Required Attempt 2 regressions

Expand the focused browser tests. At minimum prove all of these against the final production code:

1. **Root and cache**
   - root label is obtained from the real schema response;
   - first expansion of a real object type calls `browseShopifySchema`;
   - collapse/re-expand performs no second call for the cached type.

2. **Independent selection and pruning**
   - select two sibling scalar/enum leaves independently;
   - deselect one and prove the other remains;
   - deselect the final descendant and prove empty object ancestors are pruned from the selection tree.

3. **Restriction**
   - a C032-restricted field is disabled;
   - its bounded `restrictionReason` is visible;
   - it never enters the selection tree.

4. **Unsupported kinds**
   - an INTERFACE or UNION output is visibly unsupported and cannot expand/select.
   - Use the real pinned C032 graph to locate such a field/type where practical; do not special-case one in production code.

5. **Arguments**
   - a real field with arguments displays the actual argument name/type/required metadata returned by C032.

6. **Depth boundary**
   - a real-schema traversal at field depth 8 is permitted as a terminal leaf where selectable;
   - expansion that would expose depth 9 is blocked before a server Tool validation call;
   - no depth-9 leaf can enter the selection tree.
   - A recursive/cyclic path through the real Shopify graph is acceptable for reaching the boundary in the test; production code must remain generic.

7. **100-field total bound**
   - prove `selectedFieldCount()` counts both ancestors and leaves;
   - a candidate selection whose complete tree has exactly 100 nodes is allowed;
   - a candidate whose complete tree would have 101 nodes is rejected and the prior tree remains unchanged.
   - Pure selection-tree tests may construct valid `SelectionNode` values directly. React schema-page fixtures must still use the real C032 browse contract.

8. **Schema identity reset**
   - changing either `apiVersion` or `schemaHash` clears expanded type state and selection;
   - the parent status/validation path is marked stale/reset.

### Validation required on Attempt 2

Run the original required focused packet, not the shortened Attempt 1 version:

```bash
npx vitest run \
  tests/storefront-schema-browser.test.tsx \
  tests/studio-workspace.test.tsx \
  tests/discovery.test.ts \
  --reporter=verbose
```

Add a dedicated pure selection-tree test file if useful and include it in that same run.

Run targeted ESLint for every changed source/test file.

Run:

```bash
npm run typecheck
```

The existing documented unrelated baseline may remain non-zero only if no Attempt 2-owned file appears in the diagnostics. Record the exact current baseline classes.

Run:

```bash
rg -n "field\.path|selected\.includes\(field\.path\)" components src/studio
```

Expected: no Storefront schema-builder matches.

Run:

```bash
git diff --check
```

### Task/report reconciliation

Preserve the restored Out of Scope, Requirements, Dependencies, Enables, Work Items, Acceptance Criteria and Validation contract.

Mark remaining Work Items/Acceptance Criteria `[x]` only after the corrected implementation proves them.

The typecheck Validation item may be marked satisfied only under the task's explicitly allowed rule: unchanged unrelated baseline diagnostics and zero task-owned diagnostics.

Record normal Attempt 2 launcher-prepared parent/implementation worktrees, synchronization/base evidence, recursive database-submodule evidence, implementation commit, parent report commit and final clean/upstream state.

Return:

```yaml
status: review
executor: null
claimed_at: null
attempt: 2
```

and STOP.

Do not start `ARCH-021-COMMERCE-034`.

### Reviewed Files

- `src/studio/discovery/selection-tree.ts`
- `src/studio/discovery/storefront-schema-browser.tsx`
- `components/studio-workspace.tsx`
- `src/studio/testing/in-memory-studio-services.ts`
- `tests/storefront-schema-browser.test.tsx`
- `tests/studio-workspace.test.tsx`
- restored task definition and Completion Report
- parent ARCH-021 correction frontier

### Validation Reviewed

Submitted Attempt 1 evidence:

```text
focused tests: 2 files / 21 passed
lint: PASS with unrelated existing warnings
source audit: PASS
git diff --check: PASS
```

The submitted typecheck records 15 diagnostics in seven unrelated baseline files and reports no C033-owned file in those diagnostics.

The review archive does not contain `node_modules`, so the architect did not independently rerun Vitest/ESLint/typecheck.

### Architecture Conformance

Partial.

The recursive schema graph/navigation/selection architecture is conformant. The remaining non-conformance is the UI's incorrect interpretation of the accepted compiler depth and total selected-field limits.

### Follow-up

Reclaim the same task as Attempt 2.

The correction is bounded to compiler-bound parity, missing regressions and task-record reconciliation. Do not redesign the schema graph, argument-binding model or C034 query-generation contract.

`ARCH-021-COMMERCE-034` remains Pending until C033 is architect-accepted Complete.
