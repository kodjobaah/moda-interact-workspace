---
id: ARCH-021-COMMERCE-052
architecture_id: ARCH-021
title: Infer recursive Visual response trees from observed JSON
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 67
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-049
enables:
  - ARCH-021-COMMERCE-053
created: 2026-09-27
updated: 2026-09-27
---

# Infer recursive Visual response trees from observed JSON

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add one pure deterministic Commerce-local inference helper that converts an observed JSON value into one or more **browser-local `VisualAuthoringRoot` candidates** using the exact accepted COMMERCE-048/049 Visual grammar and terminology.

The helper performs no provider I/O and persists nothing. Its output is an authoring proposal only; the existing `deriveVisualTreeContract(...)` remains the sole authority that converts an accepted Visual authoring tree into canonical persisted `responseProcessing` plus Commerce `resultSchema`.

## Context

COMMERCE-048/049 establish the only Visual node vocabulary:

```text
Persisted kind   User-facing meaning
SCALAR           Scalar
OBJECT           Object
LIST             List of objects
SCALAR_LIST      List of values
```

Do not introduce another representation such as:

```text
OBJECT_LIST
LIST<object>
itemKind: OBJECT | SCALAR
```

The accepted root remains:

```text
OBJECT
LIST
```

A root primitive array is therefore not a valid Visual root in this architecture.

COMMERCE-048/049 also already own:

```text
VisualAuthoringRoot
VisualAuthoringField
VisualAuthoringNode
deriveVisualTreeContract(...)
container depth <= 4
fields/container <= 32
total projection nodes <= 128
list limit <= 20
SCALAR_LIST limit <= 20
```

Inference must build that existing authoring model; it must not invent its own persisted processing/schema generator.

## Scope

Primary implementation files:

```text
moda-interact-commerce/src/commerce/tool-authoring/visual-response-inference.ts    # new
moda-interact-commerce/src/commerce/tool-authoring/visual-result-contract.ts      # import/reuse types/helper; minimal supporting export only if required
moda-interact-commerce/tests/visual-response-inference.test.ts                     # new
```

No React file is required for this task.

## Out of Scope

- Provider/network/credential execution.
- Response-tab UI.
- Test-tab UI.
- Persisting an `AUTOMATIC` processing mode.
- Changing `VisualAuthoringRoot` semantics.
- Adding new Visual node kinds.
- Renaming `LIST`/`SCALAR_LIST`.
- Root scalar-list support.
- Arrays of arrays.
- Dynamic/map output keys.
- New scalar types beyond string/integer/number/boolean.
- Filters/sort inference.
- Guessing required fields from one observed response.
- Database/Shared changes.

## Requirements

### R1 — exact inference result contract

Export one pure helper equivalent to:

```ts
type VisualInferenceIssueCode =
  | "UNSAFE_KEY"
  | "NULL_ONLY"
  | "EMPTY_ARRAY"
  | "MIXED_ARRAY"
  | "ARRAY_OF_ARRAYS"
  | "MIXED_TYPES"
  | "MAX_DEPTH"
  | "TOO_MANY_FIELDS"
  | "TOO_MANY_NODES";

type VisualInferenceIssue = {
  path: string;
  code: VisualInferenceIssueCode;
};

type VisualInferenceCandidate = {
  resultPath: string;
  authoring: VisualAuthoringRoot;
  unresolved: VisualInferenceIssue[];
  fieldCount: number;
  nodeCount: number;
};

type VisualResponseInference = {
  candidates: VisualInferenceCandidate[];
};

inferVisualResponseTrees(observedJson: unknown): VisualResponseInference;
```

Equivalent names are acceptable. The behavior below is not.

Do not return canonical persisted `responseProcessing`/`resultSchema` as independently generated data. Candidate validity is proven by running the accepted:

```text
deriveVisualTreeContract(candidate.authoring)
```

before the candidate is returned.

### R2 — exact candidate discovery

Candidate Source paths are discovered only from values that can be Visual roots:

```text
plain object
  -> OBJECT candidate

non-empty array whose inspected concrete items are all plain objects
  -> LIST candidate
```

Never create a root candidate for:

```text
scalar
null
primitive array / SCALAR_LIST
array of arrays
mixed object/scalar array
```

Candidate paths use normal External HTTP `resultPath` dot-path semantics:

```text
root candidate -> ""
nested candidate -> "data.items"
```

Discover candidates from the root and recursively reachable safe object properties, then order candidates deterministically:

```text
root path "" first when valid
all other candidates by ascending Unicode/code-point resultPath
```

Return at most **16** candidates. Ignore additional candidates after deterministic ordering; do not randomly choose them.

Unsafe/dynamic keys are never candidate path segments.

### R3 — safe object keys map directly; do not invent names

A source object property is inferable only when the existing Visual output-name/path rules accept the key at that location.

For an inferable key:

```text
output field name = exact source key
node.path         = exact source key relative to the current parent/list row
```

Do not silently rename:

```text
product-id -> product_id
```

or otherwise guess an output name. Record `UNSAFE_KEY` and omit that field from the generated candidate.

This keeps Automatic generation deterministic and lets the author add a deliberate renamed Visual field later.

### R4 — scalar type inference

Map concrete JSON scalars exactly:

```text
string                 -> SCALAR<string>
boolean                -> SCALAR<boolean>
finite integer number  -> SCALAR<integer>
finite non-integer     -> SCALAR<number>
```

`null` alone provides no type evidence and does not become a scalar type.

When several observed values contribute to the same field:

```text
integer + integer           -> integer
integer + number            -> number
number + number             -> number
same non-number type        -> that type
different scalar categories -> MIXED_TYPES, field unresolved
```

Missing and `null` observations do not conflict with one consistent concrete type; they simply provide no additional type evidence.

Every automatically inferred field/node MUST default to:

```text
omitIfMissing: true
```

because one observed provider response cannot establish that a property is contractually required.

### R5 — object inference

A plain object field becomes:

```text
OBJECT
```

when at least one child field can be inferred within the accepted bounds.

Merge evidence from all contributing observed objects deterministically:

```text
field-name union = ascending Unicode/code-point key order
```

For each child key, collect all present values from the contributing objects and recursively apply these inference rules.

An object with zero inferable child fields is unresolved and is not emitted as an empty OBJECT node, because accepted Visual containers require fields.

### R6 — `LIST` means List of objects

A non-empty array field becomes existing kind:

```text
LIST
```

only when every inspected concrete array item is a plain object.

Use the exact COMMERCE-049 terminology:

```text
LIST -> List of objects
```

Inspect at most the first **20** source items, in source order, for structure/type inference. Merge their object-field evidence using R5.

Generated LIST settings are exactly:

```text
filters: []
sort: null
limit: 20
omitIfMissing: true
```

Do not infer filters, sort or a limit from the observed row count.

If inspected items mix object and scalar/array/null categories, do not guess: record `MIXED_ARRAY` and omit that field.

### R7 — `SCALAR_LIST` means List of values

A non-empty array field becomes existing kind:

```text
SCALAR_LIST
```

only when every inspected item is a supported non-null scalar and their types unify under R4.

Use the exact COMMERCE-049 terminology:

```text
SCALAR_LIST -> List of values
```

Generated SCALAR_LIST authoring is exactly:

```text
path: exact relative source key
resultType: inferred scalar type
limit: 20
omitIfMissing: true
```

The `resultType` exists only in the browser-local authoring node. `deriveVisualTreeContract(...)` remains responsible for placing the item type in the Commerce result schema while persisted `SCALAR_LIST` processing remains path/limit/omit-only.

### R8 — empty arrays are unresolved, not guessed

For:

```json
{ "tags": [] }
```

there is not enough evidence to decide between:

```text
LIST / List of objects
SCALAR_LIST / List of values
```

Therefore:

```text
record EMPTY_ARRAY
omit the field from the generated candidate
```

Do not generate `SCALAR_LIST` with blank item type and do not generate an empty LIST.

### R9 — arrays of arrays and null-item arrays are unsupported

The accepted C049 scope excludes arrays of arrays and null items in primitive arrays.

Therefore:

```text
[[...], [...]]        -> ARRAY_OF_ARRAYS, omit
["red", null]        -> MIXED_ARRAY, omit
[{...}, null]         -> MIXED_ARRAY, omit
```

Do not expand the Visual grammar in this task.

### R10 — bounded inference uses existing Visual limits

Do not create an independent larger Automatic grammar.

Inference must respect:

```text
max Visual container depth = 4
max fields per container    = 32
max total projection nodes  = 128
LIST/SCALAR_LIST limit      = 20
```

When source structure exceeds a bound:

```text
process deterministic ascending field/path order
retain only the portion that fits
record the corresponding bound issue
never emit an invalid VisualAuthoringRoot
```

A candidate with at least one valid field may remain usable with unresolved issues.

A candidate with no valid fields is omitted.

### R11 — deterministic authoring client IDs

Generated fields require unique browser-local `clientId` values.

Do not use randomness for inference output/tests.

Derive each ID deterministically from:

```text
candidate resultPath
+
relative output field path
```

with a fixed prefix such as:

```text
auto:
```

The exact encoding may follow repository conventions but must be stable for the same observed JSON/candidate and unique within one candidate.

### R12 — candidate validation is delegated to C048/C049

Every returned candidate must satisfy:

```ts
const derived = deriveVisualTreeContract(candidate.authoring);
derived.ok === true;
```

If derivation fails, the candidate is not returned.

Do not create a second schema derivation implementation inside inference.

### R13 — purity

The inference helper performs:

```text
zero network I/O
zero credential access
zero database I/O
zero React state mutation
zero persistence
zero time/random dependence
```

The same JSON input must produce structurally equal inference output.

## Work Items

- [x] Add a pure Visual response-inference module.
- [x] Reuse the exact COMMERCE-048/049 authoring types and terminology.
- [x] Implement deterministic root/nested candidate discovery.
- [x] Implement scalar, object, List of objects and List of values inference.
- [x] Merge consistent evidence across up to 20 object-list rows.
- [x] Emit bounded unresolved issue codes instead of guessing ambiguous structures.
- [x] Respect C048/049 field/depth/node/list bounds.
- [x] Generate deterministic browser-local client IDs.
- [x] Validate every emitted candidate through `deriveVisualTreeContract(...)`.
- [x] Add focused pure-unit regressions.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-048
  VisualAuthoringRoot / recursive OBJECT + LIST model
  deriveVisualTreeContract(...)
  depth/field/node bounds

ARCH-021-COMMERCE-049
  SCALAR_LIST persisted/authoring semantics
  exact LIST = List of objects terminology
  exact SCALAR_LIST = List of values terminology
```

Produces:

```text
VisualResponseInference
  -> candidate resultPath + existing VisualAuthoringRoot + bounded unresolved issues
```

No cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-049

## Enables

- ARCH-021-COMMERCE-053

## Acceptance Criteria

- [x] Inference uses only `SCALAR`, `OBJECT`, `LIST`, `SCALAR_LIST`.
- [x] UI/documentation terminology remains `Scalar`, `Object`, `List of objects`, `List of values`.
- [x] No `OBJECT_LIST`, `itemKind`, `LIST<object>` or parallel node grammar is introduced.
- [x] Root Visual candidate remains OBJECT/LIST only.
- [x] Root primitive arrays produce no Visual candidate.
- [x] Scalars map deterministically to string/integer/number/boolean.
- [x] Integer+number evidence widens to number; incompatible scalar categories are unresolved.
- [x] Missing/null field observations do not imply requiredness or conflict with a concrete type.
- [x] Every generated field defaults `omitIfMissing: true`.
- [x] Nested objects infer OBJECT nodes recursively.
- [x] Arrays of objects infer existing LIST / `List of objects`.
- [x] Primitive scalar arrays infer existing SCALAR_LIST / `List of values`.
- [x] Empty arrays, arrays of arrays and mixed/null-item arrays are not guessed.
- [x] LIST/SCALAR_LIST generated limit is 20, not observed length.
- [x] No filters/sort are inferred.
- [x] Unsafe keys are not silently renamed.
- [x] Candidate ordering is deterministic with root first and then ascending resultPath.
- [x] At most 16 candidates are returned.
- [x] C048/049 field/depth/node bounds are honored.
- [x] Every candidate passes `deriveVisualTreeContract(...)` before return.
- [x] Same input produces structurally equal output without clock/random/environment dependence.

## Mandatory Regression Scenarios

Add named focused tests for at least:

```text
1. {title:"Jacket"} -> root OBJECT with title SCALAR<string>.
2. {stock:2} -> integer.
3. {price:2.5} -> number.
4. {active:true} -> boolean.
5. {product:{title:"Jacket"}} -> nested OBJECT.
6. {variants:[{size:"S",available:true},{size:"M",available:false}]} -> LIST / List of objects.
7. {tags:["red","blue"]} -> SCALAR_LIST<string> / List of values.
8. {ids:[1,2,3]} -> SCALAR_LIST<integer>.
9. {scores:[1,2.5]} -> SCALAR_LIST<number>.
10. list rows with integer then number field -> number.
11. list rows with string then boolean same field -> MIXED_TYPES and field omitted.
12. list rows missing a field in some rows -> inferred field remains omitIfMissing=true.
13. null then string field evidence -> string + omitIfMissing=true.
14. null-only field -> NULL_ONLY and omitted.
15. empty array -> EMPTY_ARRAY and omitted.
16. ["red",null] -> MIXED_ARRAY and omitted.
17. [{a:1},null] -> MIXED_ARRAY and omitted.
18. [[1],[2]] -> ARRAY_OF_ARRAYS and omitted.
19. unsafe output key is omitted with UNSAFE_KEY and not renamed.
20. root primitive array -> zero candidates.
21. root array of objects -> root LIST candidate resultPath="".
22. {data:{items:[{id:1}]}} produces root OBJECT plus nested safe candidate paths in deterministic order.
23. nested LIST inside OBJECT keeps paths relative to its row/parent.
24. nested SCALAR_LIST inside LIST row uses SCALAR_LIST, not LIST.
25. more than 32 fields retains deterministic bounded subset and records TOO_MANY_FIELDS.
26. more than 128 total nodes never emits an invalid candidate.
27. fifth OBJECT/LIST container depth is omitted/flagged MAX_DEPTH.
28. more than 16 candidate roots returns exactly the deterministic first 16.
29. generated client IDs are stable and unique.
30. every emitted candidate passes deriveVisualTreeContract(...).
31. repeated invocation with identical JSON deep-equals prior result.
```

## Validation

- [x] focused `tests/visual-response-inference.test.ts`
- [ ] `npm run test:arch020-response-processing` when shared Visual assumptions are touched
- [ ] `npm run test:arch020-external-tools-ui` is **not required** unless this pure task unexpectedly changes UI-owned code
- [x] targeted ESLint on changed files
- [x] `git diff --check`
- [x] changed-file TypeScript diagnostics contain no task-owned error

## Stop Condition

After deterministic inference, candidate validation, mandatory regressions and Completion Report are complete, set the task to `review`, clear the execution claim under the normal workflow, return control to `moda_architect` and STOP. Do not begin COMMERCE-053.

## Implementation Notes

Keep the implementation pure and small. The purpose is to translate observed JSON **into the already accepted Visual authoring model**, not to create a second response-processing system.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-commerce/src/commerce/tool-authoring/visual-response-inference.ts`
- `moda-interact-commerce/tests/visual-response-inference.test.ts`

### Work Completed

- Corrected A1-R1: field-level null values are ignored while classifying scalar/list evidence; null items inside an observed array still produce `MIXED_ARRAY`.
- Corrected A1-R2: nodes are reserved before descending and rolled back when a field is omitted. `nodeCount` matches the emitted recursive tree, and the deterministic 128-node prefix remains derivable.
- Corrected A1-R3: safe source keys are traversed in sorted order until 32 inferable fields are emitted; unsafe or unresolved keys do not consume the field limit.
- Candidate limiting applies to valid derived candidates, and merged array evidence inspects at most 20 source items in source order.
- Added individually named regressions for all 31 mandatory scenarios plus Attempt 2 null/list, mixed array, aggregate item-bound, invalid-candidate-bound, and unsafe-key traversal cases.
- Every emitted candidate continues to be validated by `deriveVisualTreeContract(...)`; no persisted grammar, UI, or cross-repository contract was added.
- Reconciled Work Items, Acceptance Criteria, and Validation checkboxes. The Architect Review section was not edited.

### Validation Results

- `./node_modules/.bin/vitest run tests/visual-response-inference.test.ts`: passed, 37 tests.
- Targeted ESLint on both changed files: passed.
- Changed-file diagnostics via `get_errors`: no errors in either changed file.
- `git diff --check`: passed after the report update.
- `npm run test:arch020-response-processing` was not run because this task changed only the inference helper/tests and did not modify shared Visual assumptions or derivation code.
- `npm run test:arch020-external-tools-ui` was not run because no UI-owned files changed; the task explicitly marks that suite as not required for this pure task.

### Deviations

- None for Attempt 2.

### Assumptions

- Existing C048/C049 authoring types and `deriveVisualTreeContract(...)` remain authoritative for Visual grammar and canonical derived output.
- Prepared launcher synchronization, dependency gate, claim, and recursive submodule materialization are authoritative startup evidence.

### Unresolved Issues

- None within task scope. Repository-wide TypeScript diagnostics were not rerun; changed-file diagnostics are clean.

### Architectural Concerns

- None.

### Physical Worktree and Launch Evidence

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-052`, `task/ARCH-021-COMMERCE-052`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-052`, `task/ARCH-021-COMMERCE-052`.
- Shared workspace or shared implementation checkout switched/mutated: no. Another task worktree reused: no.
- Start synchronization: parent remote task branch fast-forwarded `not-needed`; parent origin/main incorporated `yes`; implementation remote task branch fast-forwarded `not-needed`; implementation origin/main incorporated `already-current`.
- Recursive submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; recorded `database` commit `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Attempt 2 claim commit `d1012faddac8cbec1181c82609a264e92b8b6c46` was pushed by the launcher.
- Implementation commit `0fbd643` was pushed to `origin/task/ARCH-021-COMMERCE-052`; no submodule gitlink was staged.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 is not accepted. The implementation correctly reuses the existing C048/C049 Visual authoring grammar and delegates final contract derivation to `deriveVisualTreeContract(...)`, but the submitted inference behavior and regression coverage do not yet satisfy the task contract.

1. **A1-R1 — field-level null evidence incorrectly conflicts with array evidence.** `inferNode(...)` removes `null` before deciding that a field is array-shaped, but then calls `inferArray(...)` with the original values. For merged observations such as `[{ tags: null }, { tags: ["red"] }]`, the field is therefore reported as `MIXED_ARRAY` and omitted. R4 requires missing/null field observations to provide no conflicting type evidence. Treat field-level null as no evidence for LIST/SCALAR_LIST classification while continuing to reject null *items inside an observed array* under R9. Add regressions for both scalar-list and list-of-objects evidence merged with field-level null.

2. **A1-R2 — the 128-node budget counts descendants that are not returned and can discard a parent that would fit with a bounded subset of its children.** `inferFields(...)` recursively builds a child node before reserving/counting the parent. When nested inference exhausts the budget, the parent is then skipped, leaving orphaned counts in `nodeCount`. Reserve/consume budget so only emitted projection nodes count, `nodeCount` equals the actual recursive node count in `authoring`, and deterministic traversal retains the portion that fits. Add a regression with four sorted top-level OBJECT fields each containing 32 scalar children: the returned candidate must remain valid, contain exactly 128 emitted nodes, retain the deterministic prefix of the fourth branch that fits, and report `TOO_MANY_NODES` for the truncated remainder.

3. **A1-R3 — uninferable/unsafe source keys currently consume the 32-field traversal window.** `keys.slice(0, MAX_FIELDS)` is applied before a key is proven inferable. This can hide a later safe/inferable field even though the generated container would contain fewer than 32 fields. Traverse keys in deterministic order, omit unsafe/unresolved keys without consuming emitted-field capacity, and cap the generated container at 32 actual fields. Add a regression where the first sorted source keys are unresolved/unsafe and a later valid key must still be inferred.

4. **A1-R4 — the mandatory regression contract is incomplete.** The seven broad tests cover only part of the 31 required named scenarios and several behaviors are executed without asserting the required outcome. Add explicit focused assertions for every mandatory scenario, including at minimum: mixed scalar categories produce `MIXED_TYPES` and omit the field; a genuinely missing field in some LIST rows remains optional; `[{a:1}, null]` is `MIXED_ARRAY`; a root array of objects produces a root LIST candidate; nested LIST/SCALAR_LIST paths remain relative; the >128-node case; fifth-container `MAX_DEPTH`; recursive client-id uniqueness; and `deriveVisualTreeContract(...).ok === true` for every emitted candidate.

5. **A1-R5 — the durable task record was moved to `review` with all Work Items, Acceptance Criteria and Validation checkboxes still unchecked.** On Attempt 2, reconcile those agent-owned sections with the work actually completed and leave any unsatisfied requirement unchecked. The task must not return to review until every required checkbox is truthfully satisfied or an explicit blocker is recorded.

### Reviewed Files

- `moda-interact-commerce/src/commerce/tool-authoring/visual-response-inference.ts`
- `moda-interact-commerce/tests/visual-response-inference.test.ts`
- `moda-interact-commerce/src/commerce/tool-authoring/visual-result-contract.ts`
- `docs/decisions/commerce/ARCH-021/COMMERCE-052-infer-visual-response-tree-from-observed-json.md`
- `docs/decisions/commerce/ARCH-021/_index.md`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

### Validation Reviewed

- Submitted focused result: `tests/visual-response-inference.test.ts` — 7 tests passed.
- Submitted targeted ESLint — passed.
- Submitted `git diff --check` — passed.
- Submitted changed-file TypeScript assessment — no task-owned diagnostics reported.
- Physical worktree/start synchronization evidence is present and conforms to the task-isolation protocol.
- Source review identified the A1-R1/A1-R2/A1-R3 behavioral defects and incomplete mandatory regression/task-record coverage above; no independent test rerun was required to establish these corrections.

### Architecture Conformance

Partial. The implementation keeps inference Commerce-local and pure, reuses `SCALAR` / `OBJECT` / `LIST` / `SCALAR_LIST`, introduces no parallel persisted grammar, and delegates candidate validation to `deriveVisualTreeContract(...)`. It does not yet conform to R4 null-evidence semantics, R10 deterministic field/node bounding, the Mandatory Regression Scenarios, or the repository task-record completion protocol.

### Follow-up

Return the same task through `/moda-task ARCH-021-COMMERCE-052` for Attempt 2. Implement A1-R1 through A1-R4, reconcile the agent-owned task checkboxes per A1-R5, rerun the task-required validation, update the Completion Report, set status back to `review`, clear the execution claim, and STOP. Do not begin ARCH-021-COMMERCE-053.
