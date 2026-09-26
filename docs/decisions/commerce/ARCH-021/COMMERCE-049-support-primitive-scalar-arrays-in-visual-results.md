---
id: ARCH-021-COMMERCE-049
architecture_id: ARCH-021
title: Support primitive scalar arrays in Visual response results
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 64
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-048
enables:
  - ARCH-021-COMMERCE-050
created: 2026-09-26
updated: 2026-09-26
---

# Support primitive scalar arrays in Visual response results

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Extend the accepted COMMERCE-048 recursive Visual response tree with one explicit
**list-of-values** leaf so Visual authoring can produce bounded primitive arrays such as:

```json
{
  "tags": ["red", "blue"]
}
```

without requiring JavaScript and without changing the meaning of the existing Visual
`LIST` node, which remains a list of projected objects.

The new capability must reuse the Commerce-owned result-schema, Visual derivation,
reconstruction, runtime processing, Response validation, publication and local-authoring
boundaries accepted in COMMERCE-048.

## Context

COMMERCE-048 establishes the canonical preproduction Visual grammar:

```text
SCALAR
OBJECT
LIST
```

where:

```text
SCALAR -> one scalar value
OBJECT -> one projected object
LIST   -> an array of projected objects
```

That correctly supports structures such as:

```json
{
  "title": "T-Shirt",
  "variants": [
    { "size": "S", "available": true },
    { "size": "M", "available": false }
  ]
}
```

but it cannot express this common shape:

```json
{
  "tags": ["red", "blue"]
}
```

because an existing `LIST` requires object-row fields.

The Commerce-owned `CommerceResultSchemaSchema` already supports arrays whose `items`
are scalar schemas. Therefore the missing capability is specifically the Visual
processing/authoring node, not a Shared contract or database change.

## Architectural Decision

### AD1 — add a distinct `SCALAR_LIST` Visual leaf

Do **not** overload the existing `LIST` node.

The canonical distinction is:

```text
SCALAR       -> "red"
OBJECT       -> { ... }
LIST         -> [{ ... }, { ... }]
SCALAR_LIST  -> ["red", "blue"]
```

Persist exactly one new Visual processing node kind equivalent to:

```ts
export type VisualScalarListProjection = {
  kind: "SCALAR_LIST";
  path: string;
  limit: number;
  omitIfMissing?: true;
};
```

and extend:

```ts
VisualProjectionNode
```

to include it.

`SCALAR_LIST` is a leaf. It has no nested `fields`, `filters` or `sort`.

### AD2 — item type belongs only to Commerce `resultSchema`

Do not persist an item type in `responseProcessing`.

This is prohibited:

```ts
{
  kind: "SCALAR_LIST",
  path: "tags",
  itemType: "string", // prohibited persisted duplication
  limit: 20
}
```

The browser-local authoring node carries the selected item type only so the canonical
Commerce result schema can be derived.

Use a local authoring shape equivalent to:

```ts
type VisualAuthoringScalarListNode = {
  kind: "SCALAR_LIST";
  path: string;
  resultType: "string" | "integer" | "number" | "boolean" | "";
  limit: string | number;
  omitIfMissing?: true;
};
```

The exact file/type names may follow repository conventions, but this ownership split is
mandatory.

### AD3 — root Visual shape remains OBJECT or LIST

COMMERCE-049 does not add a root primitive-array result mode.

The Visual root remains exactly:

```text
OBJECT
LIST
```

A `SCALAR_LIST` may appear as a projected field at any location where a Visual leaf is
allowed, including:

```text
root OBJECT
  tags SCALAR_LIST

root OBJECT
  product OBJECT
    tags SCALAR_LIST

root LIST
  each row
    tags SCALAR_LIST
```

provided all existing C048 container-depth/node/field bounds remain satisfied.

## Scope

Primary implementation files are expected to include:

```text
moda-interact-commerce/src/commerce/tool-definition/contracts.ts
moda-interact-commerce/src/commerce/tool-authoring/visual-result-contract.ts
moda-interact-commerce/src/commerce/external-response/index.ts
moda-interact-commerce/src/commerce/tool-authoring/external-validation.ts
moda-interact-commerce/src/commerce/tool-definition/publication.ts
moda-interact-commerce/src/studio/external-http/visual-tree-editor.tsx
moda-interact-commerce/src/studio/external-http/response-tab.tsx
moda-interact-commerce/src/studio/external-http/ports.ts        # only when local types require widening
```

Focused tests should extend the existing C048-owned suites rather than create parallel
implementations solely for C049.

If the historical:

```text
src/studio/external-http/processor.ts
```

remains unreferenced when this task executes, remove it as adjacent dead-code cleanup and
prove with repository search that no production/test caller depends on it. Do not modify
it into a second Visual runtime implementation.

## Out of Scope

- Root primitive-array Visual results such as `["red", "blue"]`.
- Filters on `SCALAR_LIST`.
- Sorting `SCALAR_LIST`.
- Arrays of arrays.
- Arrays containing objects; use existing `LIST` for object rows.
- Arrays containing `null`.
- Maps/dictionaries with dynamic output keys.
- New scalar types beyond string/integer/number/boolean.
- Unbounded item counts.
- Changes to `@modainteract/moda-interact-shared`.
- Prisma/database migrations.
- Production data compatibility/migration work; the platform remains preproduction.
- Live provider execution from Response authoring.
- Test-tab redesign or schema inference.
- Request authoring changes.
- Agent-contract/Review redesign.
- Phase 2 navigation gating.

## Exact Persisted Contract

### R1 — `SCALAR_LIST` schema

Update the Commerce-local recursive Visual contract in:

```text
src/commerce/tool-definition/contracts.ts
```

so `VisualProjectionNode` accepts exactly:

```ts
{
  kind: "SCALAR_LIST";
  path: safe non-empty Visual dot path;
  limit: integer 1..20;
  omitIfMissing?: true;
}
```

Use the same path rules as C048:

```text
safePath(path) = true
and no segment may be:
  __proto__
  prototype
  constructor
```

Reject unknown properties through the same strict-object convention as the existing
Visual nodes.

`SCALAR_LIST` counts as one projection node toward the existing C048 total-node bound.
It is a leaf and therefore does not add another Visual **container** level.

At a location where another nested OBJECT/LIST would exceed the C048 container-depth
limit, `SCALAR_LIST` remains permitted because it does not recursively contain Visual
containers.

### R2 — no processing type duplication

The persisted node MUST NOT contain:

```text
resultType
itemType
schema
itemsSchema
```

or any equivalent duplicated result-type field.

The durable item type remains represented only by the corresponding array `items`
schema in the Commerce-owned `resultSchema`.

## Authoring and Result-Schema Derivation

### R3 — browser-local authoring type

Extend the C048 authoring union with a node equivalent to:

```ts
type VisualAuthoringScalarListNode = {
  kind: "SCALAR_LIST";
  path: string;
  resultType: VisualResultType | "";
  limit: string | number;
  omitIfMissing?: true;
};
```

It participates in the existing browser-local field model with stable `clientId`.

Invalid/incomplete values must remain visible locally, including:

```text
blank item type
invalid path
blank limit
non-integer limit
limit < 1
limit > 20
```

Do not replace invalid local state with the last canonical value.

### R4 — deterministic derived schema

Extend the accepted C048 derivation helper rather than creating a separate primitive-list
derivation function.

For a valid `SCALAR_LIST`, derive:

```ts
{
  type: "array",
  items: <scalar item schema>,
  maxItems: limit
}
```

with exact item mapping:

```text
string
  -> { type: "string", maxLength: 4096 }

integer
  -> { type: "integer" }

number
  -> { type: "number" }

boolean
  -> { type: "boolean" }
```

Example authoring:

```text
Output name: tags
Type: List of values
Path: tags
Item type: string
Limit: 20
Omit if missing: false
```

must derive a result-property schema equivalent to:

```json
{
  "type": "array",
  "items": {
    "type": "string",
    "maxLength": 4096
  },
  "maxItems": 20
}
```

and persisted processing equivalent to:

```json
{
  "kind": "SCALAR_LIST",
  "path": "tags",
  "limit": 20
}
```

`omitIfMissing` continues to control parent-object requiredness exactly as in C048.

### R5 — deterministic reconstruction

Extend the accepted C048 reconstruction helper; do not create a second reconstruction
path.

For persisted:

```ts
{
  kind: "SCALAR_LIST",
  path,
  limit,
  omitIfMissing?
}
```

require the corresponding Commerce result schema to be exactly a bounded scalar array:

```text
type = array
items.type = string | integer | number | boolean
maxItems = processing.limit
```

For string items require the canonical finite `maxLength` used by C048 derivation.

Reject rather than guess when:

```text
schema is not an array
items schema is OBJECT/ARRAY
items scalar type is unsupported
string maxLength is missing/non-canonical
maxItems does not equal processing.limit
requiredness conflicts with omitIfMissing
unexpected schema keywords are present
```

Reconstruction must restore the browser-local `resultType` from the item schema.

## Runtime Processing

### R6 — exact execution semantics

Extend the accepted production recursive processor in:

```text
src/commerce/external-response/index.ts
```

Do not create a parallel scalar-array processor.

For a `SCALAR_LIST` node:

```text
1. read node.path relative to the current parent object/list row;
2. if missing:
     omitIfMissing=true -> omit property;
     otherwise          -> INVALID_RESPONSE;
3. require the present value to be an Array;
4. output at most min(node.limit, input.limits.maxSearchResults) items;
5. preserve source order exactly;
6. for every emitted item:
     check AbortSignal/deadline;
     consume one unit of the existing C048 inspected-row/item work budget;
     require a non-null primitive scalar:
       string
       finite number
       boolean
     reject object/array/null/non-finite number;
7. copy each accepted primitive into a new output array;
8. never mutate the source array.
```

The runtime processor deliberately does **not** know whether a finite number is declared
as `integer` versus `number`, or whether the selected type is string/boolean. Exact item
type validation occurs when the complete processed value is parsed through the accepted
Commerce-owned `compileCommerceResultSchema(...)` boundary.

Therefore:

```text
source primitive shape validation
  -> Visual processor

exact authored item type validation
  -> Commerce result-schema compiler
```

This separation preserves C048's rule that result types do not live in processing.

### R7 — no filters or sort in this task

`SCALAR_LIST` has no:

```text
filters
sort
fields
```

Do not emulate filters/sort by wrapping primitive values in synthetic row objects.

A later architecture task may add primitive-list filtering/sorting if a real product use
case requires it.

## Response Validation and Publication

### R8 — Response-only validation

Extend the existing COMMERCE-044/C048 Response-only validation path to understand
`SCALAR_LIST` through the canonical Visual derivation/reconstruction contract.

Validation must report deterministic nested issue paths for at least:

```text
missing result type
invalid path
invalid limit
processing/resultSchema mismatch
unsupported/non-scalar array items schema
```

It must continue to perform zero:

```text
provider HTTP
DNS
credential read/decryption
Tool/ToolRevision persistence
```

### R9 — publication compatibility

Publication compatibility must reuse the accepted C048 reconstruction/derivation helper.

Do not add a second `SCALAR_LIST` schema compatibility algorithm in publication code.

A canonical `SCALAR_LIST` processing/result-schema pair must publish exactly as another
valid Visual tree node. Mismatched processing/schema must fail closed.

### R10 — final output validation remains authoritative

All production/fixture/sample paths must continue to validate the final processed output
with:

```text
compileCommerceResultSchema(...)
```

C049 must not reintroduce Shared `DetailsSchemaSchema` or
`compileSubset(..., "details")` into Commerce result/output paths.

## Studio UI and Local State

### R11 — explicit user-facing distinction

In the Visual field type selector, make the distinction obvious.

Use labels equivalent to:

```text
Scalar
Object
List of objects
List of values
```

Do not label both object-row and primitive lists simply as `List`.

The persisted kinds remain:

```text
SCALAR
OBJECT
LIST
SCALAR_LIST
```

### R12 — exact `List of values` controls

For `SCALAR_LIST`, expose exactly the Visual authoring controls needed for this task:

```text
Output name
Source path
Item type
Limit
Omit if missing
```

Item type options are exactly:

```text
string
integer
number
boolean
```

Do not show nested projected fields, filters or sort controls.

### R13 — preserve inactive branch drafts

Extend C048 per-field branch retention so changing one field through:

```text
SCALAR
OBJECT
LIST
SCALAR_LIST
```

and returning to a previous kind restores that kind's prior browser-local draft during
the authoring session.

Example:

```text
field = LIST
  configure object-row fields
switch -> SCALAR_LIST
  path=tags itemType=string limit=10
switch -> LIST
  previous LIST fields/settings restored
switch -> SCALAR_LIST
  tags/string/10 restored
```

Inactive branch drafts are browser-local only and must never enter the canonical Tool
definition.

### R14 — stale validation and truthful disclosures

Any `SCALAR_LIST` edit must immediately make a previous Response validation success stale,
including edits that are currently invalid and cannot be promoted canonically.

When local `SCALAR_LIST` authoring is invalid:

```text
retain attempted values
show local error
suppress/mark stale derived processing/result-contract presentation
prevent Save/Create of the invalid active tree
keep Response/Test/Agent/Review navigation available
```

Do not display the last valid scalar-array schema as if it represented the current
invalid edit.

## Work Items

- [ ] Add canonical persisted `SCALAR_LIST` projection to the Commerce Visual node union.
- [ ] Extend structural/path/node validation for `SCALAR_LIST`.
- [ ] Add browser-local `SCALAR_LIST` authoring node with result type and raw limit state.
- [ ] Extend the canonical C048 derivation helper for scalar-array processing/schema output.
- [ ] Extend the canonical C048 reconstruction helper for scalar arrays.
- [ ] Execute `SCALAR_LIST` through the existing recursive production Visual processor.
- [ ] Share the existing C048 cancellation/deadline/work budget with scalar-list items.
- [ ] Extend Response-only validation and deterministic issue paths.
- [ ] Extend publication compatibility through the shared C048 helper.
- [ ] Add `List of values` UI controls and branch-draft retention.
- [ ] Preserve stale-validation/raw-local-state semantics for invalid scalar-list edits.
- [ ] Keep fixture/sample/live result validation on `compileCommerceResultSchema(...)`.
- [ ] Remove `src/studio/external-http/processor.ts` only if it is still proven unreferenced.
- [ ] Add focused contract/runtime/UI/validation/publication regressions.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-048
  canonical Commerce-owned result schema
  recursive VISUAL processing grammar
  authoring derivation/reconstruction
  recursive runtime processor
  Response-only validation integration
  publication compatibility
  local branch-draft semantics
```

Produces:

```text
one additional Commerce-local Visual projection leaf:
SCALAR_LIST
```

No cross-repository runtime contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-048

## Enables

None.

## Acceptance Criteria

- [ ] Visual authoring can produce `{ "tags": ["red", "blue"] }` without JavaScript.
- [ ] Existing `LIST` continues to mean a list of projected objects; its semantics are unchanged.
- [ ] Persisted primitive arrays use explicit `kind:"SCALAR_LIST"`.
- [ ] Persisted `SCALAR_LIST` contains path/limit/omit-if-missing only and does not duplicate item result type.
- [ ] Browser-local `SCALAR_LIST` supports string/integer/number/boolean item types.
- [ ] Derived Commerce schema is a bounded scalar array with `maxItems = limit`.
- [ ] String item schemas use the canonical bounded string maxLength.
- [ ] Reconstruction deterministically restores item type from the Commerce result schema.
- [ ] Root Visual shape remains OBJECT/LIST; no root scalar-array mode is introduced.
- [ ] Runtime paths are relative to the current parent/list row.
- [ ] Runtime preserves primitive-array source order.
- [ ] Runtime emits at most `min(limit, maxSearchResults)` values.
- [ ] Runtime rejects object, array, null and non-finite-number elements among emitted values.
- [ ] Runtime shares C048 cancellation/deadline and inspected-item/row work-budget enforcement.
- [ ] Runtime does not mutate source arrays.
- [ ] Exact item type is enforced by final Commerce result-schema validation.
- [ ] `SCALAR_LIST` has no filters/sort/nested fields in this task.
- [ ] Response validation returns deterministic scalar-list issue paths with zero provider/credential/network/persistence I/O.
- [ ] Publication reuses C048 compatibility helpers and fails mismatched scalar-list schema/processing closed.
- [ ] Studio clearly distinguishes `List of objects` from `List of values`.
- [ ] `List of values` shows path, item type, limit and omit-if-missing controls only.
- [ ] SCALAR/OBJECT/LIST/SCALAR_LIST per-field branch drafts survive kind switches.
- [ ] Invalid scalar-list edits remain visible locally and stale previous validation immediately.
- [ ] Invalid active scalar-list state cannot Save/Create but does not gate navigation.
- [ ] Direct and JavaScript behavior is unchanged.
- [ ] Shared remains unchanged at 0.14.2; no Shared/Prisma migration is introduced.
- [ ] No `DetailsSchemaSchema`/`compileSubset(...,"details")` result authority is reintroduced.

## Mandatory Regression Scenarios

Add named focused tests proving at least these cases.

### Contract / derivation / reconstruction

```text
1. OBJECT { tags: SCALAR_LIST(string,path=tags,limit=20) }
   derives processing kind SCALAR_LIST and result schema array<string> maxItems=20.

2. integer/number/boolean scalar-list item types derive their exact Commerce item schemas.

3. SCALAR_LIST processing JSON contains no itemType/resultType/schema field.

4. reconstruction restores string/integer/number/boolean item type from the corresponding array item schema.

5. reconstruction rejects object-array items schema for SCALAR_LIST.

6. reconstruction rejects nested-array items schema for SCALAR_LIST.

7. reconstruction rejects maxItems != processing.limit.

8. invalid path and limit 0/21/non-integer fail deterministically.

9. SCALAR_LIST at maximum permitted C048 container depth remains valid because it is a leaf.
```

### Runtime

```text
10. source {tags:["red","blue"]} -> output {tags:["red","blue"]}.

11. limit=1 -> output {tags:["red"]} preserving order.

12. maxSearchResults smaller than configured limit further bounds output.

13. missing required path -> INVALID_RESPONSE.

14. missing omitIfMissing path -> property omitted.

15. present non-array value -> INVALID_RESPONSE even when omitIfMissing=true.

16. emitted object/array/null/non-finite-number item -> INVALID_RESPONSE.

17. final schema rejects primitive type mismatch, e.g. authored string[] but source [1,2].

18. cancellation/deadline during scalar-array work returns the existing bounded result.

19. scalar-list items share the C048 global inspected work budget with object LIST processing.

20. source array is unchanged after success/failure.
```

### UI / local state

```text
21. type selector visibly distinguishes List of objects and List of values.

22. List of values exposes Source path, Item type, Limit and Omit if missing but no nested fields/filter/sort.

23. LIST -> SCALAR_LIST -> LIST restores the previous object-list draft.

24. SCALAR_LIST -> OBJECT -> SCALAR_LIST restores path/item type/limit.

25. blank item type and invalid limit remain visible locally with actionable errors.

26. an invalid scalar-list edit immediately makes prior Response validation success stale.

27. derived processing/schema disclosure matches current valid scalar-list state and does not show stale canonical data for invalid current edits.
```

### Validation / publication / regression

```text
28. Response-only validator accepts a valid SCALAR_LIST definition.

29. validator reports processing/schema mismatch at a deterministic nested Response path.

30. validator performs zero provider/credential/DNS/HTTP/Tool-write operations.

31. publication accepts compatible scalar-list processing/schema and rejects mismatch.

32. existing nested object-row LIST regressions remain green and unchanged.

33. Direct and JavaScript regression packets remain green.

34. repository audit confirms no Shared result-schema authority was reintroduced.
```

## Validation

Run the focused scripts already owning the C048 behavior, including at minimum the
repository-declared equivalents of:

```bash
npm run test:arch021-commerce-tool-contract
npm run test:arch021-external-tool-authoring-validation
npm run test:arch020-external-tools-ui
```

Run the focused response-processing/result-schema/publication/preview/New Tool suites
that cover changed files, using the actual scripts present in `package.json`.

Then run:

```bash
npm run typecheck
npm run lint
git diff --check
```

If repository-wide typecheck remains non-zero only because of established unrelated
baseline diagnostics, record the exact count/files and prove no diagnostic names a
C049-modified source/test file.

Run source audits proving:

```text
SCALAR_LIST is present only in Commerce-local Visual/result code
no Shared source/package/gitlink changed
no Prisma migration changed
no DetailsSchemaSchema or compileSubset(...,"details") result authority was reintroduced
no second scalar-array runtime/derivation/reconstruction implementation was added
```

If `src/studio/external-http/processor.ts` is deleted, record repository-search proof
that it had no remaining import/caller before deletion.

## Stop Condition

After the canonical `SCALAR_LIST` processing node, Commerce result-schema derivation and
reconstruction, recursive runtime execution, Response validation, publication, Visual UI
and required regressions are complete, set the task to `review`, complete the Completion
Report and STOP.

Do not continue into root scalar-array results, primitive-list filters/sort, arrays of
arrays, Test-tab redesign, live-provider authoring or another unrelated Visual feature.

## Implementation Notes

Keep this task narrow. C048 already established the recursive tree and Commerce-owned
result-schema architecture. C049 should extend those accepted seams rather than create new
ones.

Prefer changing the existing discriminated unions/switches and recursive helper branches
for one new leaf kind. If implementation pressure suggests introducing a second Visual
processor, second schema compiler, or separate primitive-list publication validator, stop
and return the architectural concern instead.

## Completion Report

### Status
Ready for Review

### Files Changed
- `moda-interact-commerce/src/commerce/tool-definition/contracts.ts`
- `moda-interact-commerce/src/commerce/tool-authoring/visual-result-contract.ts`
- `moda-interact-commerce/src/commerce/external-response/index.ts`
- `moda-interact-commerce/src/studio/external-http/visual-tree-editor.tsx`
- `moda-interact-commerce/src/studio/external-http/response-tab.tsx`
- `moda-interact-commerce/src/studio/external-http/processor.ts` (deleted; pre-delete search found only its own declaration and no callers)
- `moda-interact-commerce/tests/arch021-commerce-tool-contract.test.ts`
- `moda-interact-commerce/tests/visual-result-contract.test.ts`
- `moda-interact-commerce/tests/response-processing.test.ts`
- `moda-interact-commerce/tests/external-tool-authoring-validation.test.ts`
- `moda-interact-commerce/tests/external-tools-ui.test.tsx`
- `moda-interact-commerce/tests/external-publication.test.ts`

### Work Completed
- Added strict Commerce-local `SCALAR_LIST` processing with bounded path/limit/omit settings; it remains a leaf and does not persist an item type.
- Extended the canonical C048 authoring derivation/reconstruction path for string, integer, number and boolean arrays, exact `maxItems`, canonical string bounds, requiredness, and fail-closed schema matching.
- Extended the production recursive projector to preserve order, cap items by `min(limit, maxSearchResults)`, reject null/non-primitives/non-finite numbers, check cancellation/deadline per emitted item, share the existing work budget, and leave source arrays unchanged.
- Added “List of objects” / “List of values” authoring controls, local item type/raw limit state, per-kind branch retention, stale validation behavior, and truthful invalid-state disclosures. Root shape remains OBJECT/LIST.
- Covered Response-only acceptance and deterministic mismatch paths, publication acceptance/rejection, and the existing Commerce result-schema validation boundary.
- Kept Shared pinned at `@modainteract/moda-interact-shared@0.14.2`; no Shared, Prisma, migration, or dependency-manifest changes.
- Implementation commit `99330e4` (`feat(commerce): support scalar arrays in Visual results`) was pushed to `origin/task/ARCH-021-COMMERCE-049`.

### Validation Results
- `npm run test:arch021-commerce-tool-contract`: passed, 17 tests.
- `npm run test:arch021-external-tool-authoring-validation`: passed, 50 tests across the authoring-validation and server-action suites.
- `npm run test:arch020-external-tools-ui`: passed, 35 tests.
- `npm run test:arch020-external-publication`: passed, 14 tests.
- `npm run test:arch020-response-processing`: passed, 12 tests.
- `npx vitest run tests/visual-result-contract.test.ts`: passed, 12 tests.
- `npm run test:arch020-external-preview`: passed, 19 tests.
- `npm run test:arch020-code-processor`: passed, 6 tests.
- `npm run typecheck`: non-zero with 251 diagnostics in 22 files; no diagnostic names any C049-modified file. The diagnostics are in `app/api/studio/code-response/validate/route.ts`, `auth.ts`, `lib/auth/development-platform-admin.ts`, `lib/auth/merchant-binding.ts`, `lib/discovery/compiler.ts`, `lib/server/connections.ts`, `scripts/validate-shopify-admin-local.ts`, `src/commerce/agent-configuration/prompt-service.ts`, `src/commerce/connections/command-kernel.ts`, `src/commerce/integration/backend.ts`, `src/commerce/integration/backend/c20-test-fixture.ts`, `src/commerce/integration/backend/publication-storage.ts`, `src/commerce/integration/studio/services.ts`, `tests/agent-configuration-effective.test.ts`, `tests/agent-configuration-prompts-postgres.test.ts`, `tests/auth-merchant-access-postgres.test.ts`, `tests/backend-postgres-rehearsal.test.ts`, `tests/c20-integration-fixture.test.ts`, `tests/external-credentials-postgres.test.ts`, `tests/external-wiring.test.ts`, `tests/local-external-mcp-diagnostic.test.ts`, and `tests/selected-shop-context.test.ts`.
- `npm run lint`: passed with zero errors and six warnings in unrelated existing files (`scripts/code-runtime-manifest.mjs`, `src/studio/code-response/code-response-panel.tsx`, `tests/agent-configuration-model.test.ts`, and `tests/mcp-service.test.ts`).
- `git diff --check`: passed. Source audits confirmed no details-subset result authority, no Shared/database/dependency changes, and no remaining `processVisualSample` caller. `npm run code-runtime:package` packaged the locked QuickJS runtime before validation.
- Direct/JavaScript regression suites passed: external preview 19/19 and code response processor 6/6.

### Deviations
- The first full authoring-validation run exposed a missing packaged QuickJS worker artifact after dependency installation; running the repository-declared `npm run code-runtime:package` resolved it, and the complete suite then passed.
- Repository-wide typecheck remains blocked by the 251 diagnostics listed above; diagnostics were checked against every modified source and test file and none are C049-related.

### Assumptions
- Existing C048 bounds, cancellation/deadline checks, result-schema compiler, Response-only boundary and publication reconstruction remain authoritative; C049 adds only a primitive-array leaf.
- The prepared launcher handoff owns task-branch and recursive-submodule synchronization; implementation was performed in the dedicated task worktree only.

### Unresolved Issues
- Repository-wide typecheck must be reconciled outside this bounded task; see the exact 22-file diagnostic list above.

### Architectural Concerns
- None. No second Visual runtime, derivation, reconstruction, or publication compatibility implementation was introduced.

### Physical Worktree and Launch Evidence
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-049`, `task/ARCH-021-COMMERCE-049`; launcher claim commit `4ace02f2` was already pushed before implementation.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-049`, `task/ARCH-021-COMMERCE-049`.
- Prepared-task handoff confirmed COMMERCE-048 dependency completion and synchronized the dedicated task branches/submodules. No shared workspace checkout or shared implementation checkout was switched or edited for this work; no other task worktree was reused.
- Implementation commit `99330e4` is pushed to the same-name remote task branch. No submodule gitlink was staged.

## Architect Review

### Review Status
Accepted — Attempt 1

### Review Notes
Reviewed implementation `99330e4` and parent report `236cb8ae` against the complete C049 contract and the accepted C048 recursive Visual/result-schema architecture. Accepted.

The implementation is correctly bounded to one new primitive-array Visual leaf:

- persisted `SCALAR_LIST` owns only source path, bounded limit and optional omit-if-missing; item result type is not duplicated into processing;
- C048's single derivation/reconstruction path now derives and reconstructs string/integer/number/boolean array schemas through Commerce-owned `CommerceResultSchemaSchema`;
- the production recursive Visual processor executes scalar arrays in source order, shares the existing deadline/cancellation/work budget, does not mutate source arrays, and leaves exact authored type enforcement to final Commerce result-schema validation;
- Response-only validation and publication reuse the canonical C048 Visual/result helpers rather than introducing parallel scalar-list compatibility code;
- Studio distinguishes `List of objects` from `List of values`, exposes only path/item-type/limit/omit controls for `SCALAR_LIST`, preserves per-kind browser-local drafts and invalid raw edits, and stales prior validation on invalid scalar-list edits;
- the historical duplicate Studio sample projector was removed after repository search established that the active synthetic path already delegates to the production processor;
- Shared remains pinned at 0.14.2, and no Prisma/schema migration, live provider authoring I/O or Phase 2 navigation gating was introduced.

Manual review found a separate Response-validation presentation defect: when the current Visual authoring tree is locally invalid (for example a Scalar field remains at `Choose type`) and the user presses **Validate response**, `response-tab.tsx` sends `null` for the non-canonical `responseProcessing` / `resultSchema` placeholders. The server then returns raw schema diagnostics such as `expected object, received null` and `Invalid input`. This does not invalidate the C049 scalar-array implementation, because the current local authoring error is correctly retained and C049's scalar-list functionality is complete, but the default validation UI does not clearly identify the affected field or corrective action. That cross-Visual diagnostic-presentation issue is materialised as the small follow-up `ARCH-021-COMMERCE-050`.

### Reviewed Files
- `src/commerce/tool-definition/contracts.ts`
- `src/commerce/tool-authoring/visual-result-contract.ts`
- `src/commerce/external-response/index.ts`
- `src/commerce/tool-authoring/external-validation.ts`
- `src/commerce/tool-definition/publication.ts`
- `src/studio/external-http/visual-tree-editor.tsx`
- `src/studio/external-http/response-tab.tsx`
- focused C049 contract/derivation/runtime/validation/publication/UI tests
- C049 Completion Report

### Validation Reviewed
Accepted submitted evidence:

```text
Commerce Tool contract                     17 passed
External authoring validation/actions       50 passed
External UI                                 35 passed
External publication                        14 passed
Response processing                         12 passed
Visual result contract                      12 passed
External preview                            19 passed
Code response processor                      6 passed
Focused total                              165 passed
lint                                         0 errors / 6 unrelated warnings
git diff --check                            passed
C049-owned TypeScript diagnostics            none reported
repository typecheck baseline              251 diagnostics / 22 unrelated files
Shared/result-schema ownership audits        passed
```

The supplied review archive does not include installed dependencies, so dependency-backed commands were not falsely claimed as independently rerun by the architect. Source/test inspection confirms the C049 implementation seams and focused regressions described above.

### Architecture Conformance
Conforms. C049 adds one Commerce-local `SCALAR_LIST` leaf through the accepted C048 processing/schema/runtime/validation/publication seams without changing object-row `LIST`, Shared contracts, persistence infrastructure or provider-authoring authority.

### Follow-up
`ARCH-021-COMMERCE-050` is promoted to `ready` to make Response validation diagnostics field-specific and corrective instead of exposing raw schema/Zod diagnostics when browser-local Response authoring is invalid.
