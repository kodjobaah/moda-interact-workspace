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
status: ready
priority: 67
executor: null
claimed_at: null
attempt: 0
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

- [ ] Add a pure Visual response-inference module.
- [ ] Reuse the exact COMMERCE-048/049 authoring types and terminology.
- [ ] Implement deterministic root/nested candidate discovery.
- [ ] Implement scalar, object, List of objects and List of values inference.
- [ ] Merge consistent evidence across up to 20 object-list rows.
- [ ] Emit bounded unresolved issue codes instead of guessing ambiguous structures.
- [ ] Respect C048/049 depth/field/node/list bounds.
- [ ] Generate deterministic browser-local client IDs.
- [ ] Validate every emitted candidate through `deriveVisualTreeContract(...)`.
- [ ] Add focused pure-unit regressions.

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

- [ ] Inference uses only `SCALAR`, `OBJECT`, `LIST`, `SCALAR_LIST`.
- [ ] UI/documentation terminology remains `Scalar`, `Object`, `List of objects`, `List of values`.
- [ ] No `OBJECT_LIST`, `itemKind`, `LIST<object>` or parallel node grammar is introduced.
- [ ] Root Visual candidate remains OBJECT/LIST only.
- [ ] Root primitive arrays produce no Visual candidate.
- [ ] Scalars map deterministically to string/integer/number/boolean.
- [ ] Integer+number evidence widens to number; incompatible scalar categories are unresolved.
- [ ] Missing/null field observations do not imply requiredness or conflict with a concrete type.
- [ ] Every generated field defaults `omitIfMissing: true`.
- [ ] Nested objects infer OBJECT nodes recursively.
- [ ] Arrays of objects infer existing LIST / `List of objects`.
- [ ] Primitive scalar arrays infer existing SCALAR_LIST / `List of values`.
- [ ] Empty arrays, arrays of arrays and mixed/null-item arrays are not guessed.
- [ ] LIST/SCALAR_LIST generated limit is 20, not observed length.
- [ ] No filters/sort are inferred.
- [ ] Unsafe keys are not silently renamed.
- [ ] Candidate ordering is deterministic with root first and then ascending resultPath.
- [ ] At most 16 candidates are returned.
- [ ] C048/049 field/depth/node bounds are honored.
- [ ] Every candidate passes `deriveVisualTreeContract(...)` before return.
- [ ] Same input produces structurally equal output without clock/random/environment dependence.

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

- [ ] focused `tests/visual-response-inference.test.ts`
- [ ] `npm run test:arch020-response-processing` when shared Visual assumptions are touched
- [ ] `npm run test:arch020-external-tools-ui` is **not required** unless this pure task unexpectedly changes UI-owned code
- [ ] targeted ESLint on changed files
- [ ] `git diff --check`
- [ ] changed-file TypeScript diagnostics contain no task-owned error

## Stop Condition

After deterministic inference, candidate validation, mandatory regressions and Completion Report are complete, set the task to `review`, clear the execution claim under the normal workflow, return control to `moda_architect` and STOP. Do not begin COMMERCE-053.

## Implementation Notes

Keep the implementation pure and small. The purpose is to translate observed JSON **into the already accepted Visual authoring model**, not to create a second response-processing system.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

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

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
