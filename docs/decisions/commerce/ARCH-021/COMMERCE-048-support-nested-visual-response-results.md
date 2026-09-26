---
id: ARCH-021-COMMERCE-048
architecture_id: ARCH-021
title: Support nested Visual response result trees
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 63
executor: copilot
claimed_at: 2026-09-26T18:55:02Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-045
enables: []
created: 2026-09-26
updated: 2026-09-26
---

# Support nested Visual response result trees

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Extend External HTTP Visual response authoring from the current flat scalar projection model to a bounded recursive result tree that can produce nested objects and nested lists while preserving the accepted legacy flat OBJECT/LIST definitions, deterministic derived `resultSchema`, zero-provider-I/O Response validation, sandbox-independent Visual execution and all C045 local-authoring invariants.

The required first-class use case is an object containing an embedded list, for example:

```json
{
  "title": "T-Shirt",
  "price": 20,
  "variants": [
    {
      "size": "S",
      "available": true
    },
    {
      "size": "M",
      "available": false
    }
  ]
}
```

Visual authoring must be able to construct that result without requiring JavaScript.

## Context

The accepted COMMERCE-043/C045 Visual contract is deliberately flat:

```text
root OBJECT
  -> scalar projected fields

or

root LIST
  -> list of rows
  -> scalar projected fields
  -> canonical root result envelope { items: [...] }
```

Current implementation constraints include:

```text
src/commerce/tool-authoring/visual-result-contract.ts
  VISUAL_RESULT_TYPES = string | integer | number | boolean

src/commerce/external-response/index.ts
  projectRow(...)
    -> rejects any projected value that is not scalar

@modainteract/moda-interact-shared/commerce
  VisualResponseProcessingSchema
    -> legacy flat OBJECT/LIST processing only
```

The current model therefore cannot represent:

```text
OBJECT
  variants -> LIST

OBJECT
  vendor -> OBJECT

LIST
  each row
    variants -> LIST
```

JavaScript response processing can express those shapes, but Visual rules cannot.

This task adds one Commerce-owned recursive Visual processing representation. It does **not** change the Shared package, does not require a database migration and does not remove support for already-persisted legacy OBJECT/LIST definitions.

## Architectural Decision

### AD1 — Shared remains pinned and unchanged

Keep exactly:

```json
"@modainteract/moda-interact-shared": "0.14.2"
```

Do not edit/publish `moda-interact-shared` and do not change the Shared gitlink.

The existing Shared `VisualResponseProcessingSchema` remains the parser/type source for **legacy** flat OBJECT/LIST definitions only.

The recursive representation is Commerce-owned under:

```text
src/commerce/tool-definition/
src/commerce/tool-authoring/
```

### AD2 — add one new persisted processing kind; do not mutate the legacy encoding

Add a new Commerce-local processing kind:

```text
kind: "VISUAL"
```

Do **not** reinterpret the existing Shared OBJECT/LIST field grammar as recursive.

The canonical new representation is:

```ts
export type VisualTreeResponseProcessing =
  | {
      kind: "VISUAL";
      shape: "OBJECT";
      fields: Record<string, VisualProjectionNode>;
    }
  | {
      kind: "VISUAL";
      shape: "LIST";
      fields: Record<string, VisualProjectionNode>;
      filters: VisualFilter[];
      sort: VisualSort | null;
      limit: number;
    };
```

A projected field is exactly one of:

```ts
export type VisualScalarProjection = {
  kind: "SCALAR";
  path: string;
  omitIfMissing?: true;
};

export type VisualObjectProjection = {
  kind: "OBJECT";
  path: string;
  fields: Record<string, VisualProjectionNode>;
  omitIfMissing?: true;
};

export type VisualListProjection = {
  kind: "LIST";
  path: string;
  fields: Record<string, VisualProjectionNode>;
  filters: VisualFilter[];
  sort: VisualSort | null;
  limit: number;
  omitIfMissing?: true;
};

export type VisualProjectionNode =
  | VisualScalarProjection
  | VisualObjectProjection
  | VisualListProjection;
```

The top-level source is still selected by:

```text
execution.resultPath   // user-facing Source path
```

Therefore the root VISUAL object/list does not have its own `path` or `omitIfMissing`.

### AD3 — persisted processing does not duplicate scalar result types

Do not add `resultType`, JSON-schema `type`, `maxLength` or equivalent scalar result metadata to persisted `responseProcessing` nodes.

Preserve the COMMERCE-043 ownership rule:

```text
responseProcessing
  owns how source data is selected/projected

resultSchema
  owns the durable output type contract
```

The browser authoring model may carry scalar result types while editing, but canonical persisted processing strips those authoring-only types.

### AD4 — legacy definitions remain executable

`LocalResponseProcessingSchema` must accept all of:

```text
DIRECT
legacy Shared OBJECT
legacy Shared LIST
new Commerce VISUAL
JAVASCRIPT
```

Existing immutable/published legacy OBJECT/LIST Tool revisions must continue to validate and execute with unchanged semantics.

Do not run a PostgreSQL/data migration.

Do not rewrite an untouched persisted legacy DRAFT merely because an administrator opened the editor.

When a legacy Visual DRAFT is actually edited and successfully saved after this task, it may be canonicalised to `kind: "VISUAL"` through the accepted authoring-tree conversion. New Visual authoring after this task must use `kind: "VISUAL"`.

## Exact Persisted Contract

### R1 — local recursive Zod schemas

Implement the new schema in:

```text
src/commerce/tool-definition/contracts.ts
```

or a Commerce-local module imported by `contracts.ts` when doing so keeps the contract file readable.

Use `z.lazy(...)` for recursive nodes.

The persisted rules are:

```text
output field name
  safeName(...)

all source paths
  non-empty safe dot paths
  every segment must also reject:
    __proto__
    prototype
    constructor

fields per OBJECT/LIST container
  minimum 1
  maximum 32

LIST filters
  maximum 8

LIST limit
  integer
  minimum 1
  maximum 20

sort direction
  ASC | DESC
```

Filter operators remain exactly the existing accepted set:

```text
EQ
NE
GT
GTE
LT
LTE
CONTAINS
STARTS_WITH
IN
```

Filter scalar values remain exactly:

```text
string
finite number
boolean
null
```

`IN` remains:

```text
1..20 values
all values same scalar type
```

Do not add regex, arbitrary predicates, expressions or JavaScript to Visual filters.

### R2 — bounded recursive structure

Reject a canonical VISUAL processing tree when any of these bounds is exceeded:

```text
maximum container depth:        4
maximum fields per container:   32
maximum total projection nodes: 128
maximum filters per LIST:       8
maximum configured LIST limit:  20
```

Depth definition is exact:

```text
root OBJECT/LIST container = depth 1
nested OBJECT/LIST field   = parent depth + 1
SCALAR leaves do not add container depth
```

Therefore this is valid:

```text
root OBJECT                 depth 1
  product OBJECT            depth 2
    variants LIST           depth 3
      option OBJECT         depth 4
        name SCALAR
```

A nested OBJECT/LIST below `option` is invalid because it would create container depth 5.

The total-node count includes every SCALAR, OBJECT and LIST field node below the root, but not the root container itself.

Return deterministic schema/authoring diagnostics rather than overflowing recursion or silently truncating the tree.

## Authoring Contract and Derived Schema

### R3 — one browser-local typed authoring tree

Replace the current flat `visualTypes`/parallel scalar-type mapping as the primary new Visual model with one typed browser-local authoring tree.

Use a shape equivalent to:

```ts
type VisualAuthoringScalarNode = {
  kind: "SCALAR";
  path: string;
  resultType: "string" | "integer" | "number" | "boolean";
  omitIfMissing?: true;
};

type VisualAuthoringObjectNode = {
  kind: "OBJECT";
  path: string;
  fields: VisualAuthoringField[];
  omitIfMissing?: true;
};

type VisualAuthoringListNode = {
  kind: "LIST";
  path: string;
  fields: VisualAuthoringField[];
  filters: VisualFilterDraft[];
  sort: VisualSortDraft | null;
  limit: string | number;
  omitIfMissing?: true;
};

type VisualAuthoringField = {
  clientId: string; // browser-only; never persisted
  name: string;
  node: VisualAuthoringNode;
};
```

The exact TypeScript placement/name may follow repository conventions, but these semantics are mandatory.

Use an **array** for raw local authoring fields rather than a `Record` so temporarily invalid states can remain visible, including:

```text
blank output name
duplicate output name
invalid output name
blank/invalid source path
incomplete nested container
incomplete scalar result type
```

Only a valid authoring tree is converted into canonical `Record<string, ...>` processing.

`clientId` is UI-only and must never enter Tool-definition JSON, audit payloads or persistence.

### R4 — derive processing and resultSchema from the same authoring tree

Evolve the Commerce-owned Visual contract helper so one function derives both canonical artifacts from the same valid authoring tree.

Provide one canonical helper equivalent to:

```ts
deriveVisualTreeContract(authoringRoot)
  ->
  | {
      ok: true;
      processing: VisualTreeResponseProcessing;
      schema: SubsetSchema;
    }
  | {
      ok: false;
      code: VisualTreeDerivationErrorCode;
      path: string;
      message: string;
    }
```

Do not independently derive processing and schema in separate UI handlers.

The helper must:

1. validate all structural bounds;
2. reject duplicate/unsafe output names;
3. validate source paths;
4. strip authoring-only `resultType` and `clientId` from processing;
5. derive the exact recursive `resultSchema`;
6. validate the derived schema with `DetailsSchemaSchema` before returning success.

Keep existing COMMERCE-043 legacy helpers where required for compatibility, but do not maintain a second recursive derivation algorithm.

### R5 — exact recursive result-schema rules

Scalar fields derive exactly:

```text
string
  { type: "string", maxLength: 4096 }

integer
  { type: "integer" }

number
  { type: "number" }

boolean
  { type: "boolean" }
```

Every Visual OBJECT node derives a closed object:

```ts
{
  type: "object",
  properties: { ...children },
  required: [...children whose omitIfMissing !== true],
  additionalProperties: false
}
```

Every **nested** Visual LIST field derives a raw array:

```ts
{
  type: "array",
  items: <closed object schema derived from that LIST's fields>,
  maxItems: list.limit
}
```

The **root** `shape: "LIST"` preserves the accepted external result envelope:

```ts
{
  type: "object",
  properties: {
    items: {
      type: "array",
      items: <closed object schema derived from root LIST fields>,
      maxItems: root.limit
    }
  },
  required: ["items"],
  additionalProperties: false
}
```

Do not wrap nested LIST fields in `{ items: [...] }`.

This distinction is mandatory:

```text
root LIST     -> { items: [...] }
nested LIST   -> [...]
```

### R6 — deterministic reconstruction from persisted definitions

Provide one canonical reconstruction helper equivalent to:

```ts
reconstructVisualAuthoringTree(processing, resultSchema)
```

It must support both:

```text
legacy OBJECT/LIST + compatible resultSchema
new VISUAL + compatible resultSchema
```

For legacy processing, reconstruct an equivalent flat authoring tree with SCALAR nodes and preserve legacy:

```text
filters
sort
limit
omitIfMissing
source paths
```

For new VISUAL processing, recursively match every processing node against the corresponding schema node and reconstruct each SCALAR `resultType`.

Reject rather than guess when any mismatch exists, including:

```text
processing field missing from schema
schema field missing from processing
required/omitIfMissing mismatch
OBJECT processing paired with non-object schema
nested LIST paired with non-array schema
root LIST without the { items: [...] } envelope
unsupported scalar schema type
string schema without a finite maxLength
LIST schema maxItems < processing.limit
unsafe/invalid processing path
unexpected additional schema properties
```

For backward compatibility, a persisted LIST schema with:

```text
maxItems >= processing.limit
```

is reconstructable, matching COMMERCE-043/044 behavior. Newly derived canonical schemas use exactly `maxItems = processing.limit`.

No silent coercion or default type guessing is allowed.

## Runtime Processing

### R7 — use one recursive processor implementation

Update:

```text
src/commerce/external-response/index.ts
```

to execute both legacy flat Visual definitions and the new VISUAL tree through one canonical recursive processing algorithm.

Do not keep one old flat projection implementation plus a separate unrelated nested implementation.

Adapt legacy OBJECT/LIST processing in memory to the recursive execution representation, then use the same recursive projector.

DIRECT and JAVASCRIPT execution remain unchanged.

### R8 — exact path semantics

`execution.resultPath` selects the root input before Visual processing.

Within the Visual tree:

```text
SCALAR.path
OBJECT.path
LIST.path
filter.path
sort.path
```

are all relative to the current source object/list row at that node.

Example:

```json
provider source after Source path:
{
  "product": {
    "title": "T-Shirt",
    "variants": [
      { "size": "S", "available": true },
      { "size": "M", "available": false }
    ]
  }
}
```

Authoring tree:

```text
root OBJECT
  title
    SCALAR path=product.title type=string

  variants
    LIST path=product.variants limit=20
      size
        SCALAR path=size type=string
      available
        SCALAR path=available type=boolean
```

Produces:

```json
{
  "title": "T-Shirt",
  "variants": [
    { "size": "S", "available": true },
    { "size": "M", "available": false }
  ]
}
```

### R9 — missing/wrong-shape semantics

For every projected field node:

```text
path does not exist + omitIfMissing === true
  -> omit that output property

path does not exist + omitIfMissing !== true
  -> INVALID_RESPONSE

SCALAR path exists but value is not scalar
  -> INVALID_RESPONSE

OBJECT path exists but value is not a non-array object
  -> INVALID_RESPONSE

LIST path exists but value is not an array
  -> INVALID_RESPONSE
```

`omitIfMissing` applies only to an absent path. It must not convert a present wrong-shaped value into omission.

Preserve the current scalar definition:

```text
string | finite number | boolean | null
```

Final `resultSchema` validation remains authoritative for whether a scalar value satisfies the configured non-null output type.

Do not mutate provider/source objects while projecting.

### R10 — nested LIST processing semantics

Every LIST node uses the same accepted operation order:

```text
source array
  -> validate row objects / hard row bound
  -> filters (AND)
  -> stable sort
  -> configured/runtime limit
  -> recursive field projection
```

Filters and sort inspect the raw list row before projection.

Keep existing comparison semantics exactly:

```text
EQ / NE
  same scalar type required

CONTAINS / STARTS_WITH
  strings only

GT / GTE / LT / LTE
  finite numbers only

IN
  same-type scalar membership

sort
  one consistent number or string type
  stable ties
  missing/null values last for ASC and DESC
  strings compare by Unicode code point order
```

Nested LIST output is a raw array.

Root LIST output remains:

```json
{ "items": [...] }
```

### R11 — execution resource bounds remain hard

Keep existing Visual bounds and add a recursive work budget.

Per LIST node:

```text
maximum source rows accepted: 1000
configured limit:             1..20
effective emitted limit:      min(node.limit, input.limits.maxSearchResults)
```

Across the entire recursive invocation:

```text
maximum list rows inspected: 4096
```

Count each raw row considered by any root/nested LIST against that shared invocation budget.

If the structural or runtime work budget is exceeded, fail closed with the existing bounded Visual failure contract; do not partially return a truncated tree beyond the configured list-limit semantics.

Continue checking cancellation/deadline at least once every 32 row/node visits and before descending into a nested container.

The recursive implementation must not use unbounded recursion beyond R2's depth limit.

### R12 — final schema validation remains mandatory

Do not rely on projection alone for output type correctness.

The existing executor path must continue to run:

```text
compileSubset(execution.resultSchema, "details").safeParse(processed.values)
```

against the complete nested result before returning an OK Commerce Tool result.

## Studio / Response UI

### R13 — recursive Visual editor component, not more monolithic ResponseTab JSX

Do not add the recursive tree directly as another large block inside `response-tab.tsx`.

Create a focused component/module under:

```text
src/studio/external-http/
```

with repository-conventional naming, for example:

```text
visual-tree-editor.tsx
```

`ResponseTab` owns mode composition, validation state and canonical promotion. The Visual tree component owns recursive field/container editing.

Keep the component API data-oriented. Do not pass persistence services, credentials, provider clients or Server Actions into nested row components.

### R14 — exact field type choices

The Visual field type selector must expose exactly:

```text
string
integer
number
boolean
object
list
```

Interpret them as:

```text
string/integer/number/boolean
  -> SCALAR authoring node with matching resultType

object
  -> OBJECT authoring node

list
  -> LIST authoring node
```

For an OBJECT/LIST field, display its nested children immediately below/within the field with clear indentation/boundary styling.

For LIST fields also display the list's own:

```text
Limit
Sort path
Sort direction
Filters
```

at that list node. Do not reuse the root list controls to configure nested lists.

### R15 — deterministic defaults for newly-created nested containers

When a field is first changed to `object`, initialize its local OBJECT draft with exactly one child:

```text
Output name: value
Path:        value
Type:        string
Omit:        false
```

When first changed to `list`, initialize its local LIST draft with:

```text
fields:
  value -> path=value, type=string, omit=false
filters: []
sort:    null
limit:   20
```

These defaults are browser-local until the full Visual tree derives successfully.

### R16 — preserve local drafts across nested type switches

Within one authoring session, changing one field among:

```text
scalar
object
list
```

must not silently destroy the previous local draft for that field.

Key the retained browser-local branch drafts by the field's UI-only `clientId`, not by mutable output name.

Required interaction proof:

```text
field variants = LIST with two children
switch variants -> OBJECT
edit OBJECT child
switch variants -> LIST
previous LIST children/settings are restored
switch variants -> OBJECT
previous OBJECT child is restored
```

Only the currently selected branch enters canonical processing/schema derivation.

Inactive branch drafts are never persisted.

### R17 — preserve independent root OBJECT/LIST drafts

Consume the accepted C045 root-shape behavior:

```text
root OBJECT draft
root LIST draft
```

Switching root Shape must preserve each draft independently.

C048 must not regress this back into copying OBJECT fields into LIST or vice versa.

### R18 — invalid nested edits remain visible locally

The UI must retain and display invalid nested authoring values such as:

```text
blank/duplicate output names
invalid nested paths
missing scalar type
invalid nested LIST limit
invalid filter values
excess depth/node count
```

Do not silently revert to the previous canonical tree.

When the active Visual authoring tree is invalid:

```text
canonical Tool definition remains at the last valid Visual value
Save/Create remains unavailable for that active invalid Visual state
other authoring tabs remain freely navigable
```

No Phase 2 progression gating is introduced.

### R19 — processing/result-contract disclosures must describe the current state truthfully

For a valid current Visual authoring tree:

```text
View Visual processing JSON
  -> show the current canonical kind:"VISUAL" processing

View derived result contract JSON
  -> show the current derived recursive resultSchema
```

When the raw local Visual tree is invalid, do not present the previous canonical JSON as though it describes the current edit.

Either hide the disclosure or label it explicitly as:

```text
Last valid canonical processing
Last valid derived result contract
```

and show the local validation reason.

### R20 — Response-only validation understands recursive Visual authoring

Extend COMMERCE-044's Response-only validator to accept/validate the new canonical `kind:"VISUAL"` contract.

It must validate recursively and return deterministic issue paths, for example:

```text
/execution/responseProcessing/fields/variants/path
/execution/responseProcessing/fields/variants/fields/size/path
/execution/responseProcessing/fields/variants/filters/0/path
/execution/responseProcessing/fields/variants/limit
/execution/resultSchema/properties/variants/items/properties/size
```

Use the shared Commerce-owned derive/reconstruct helpers rather than implementing a separate recursive compatibility algorithm in validation.

Validation remains:

```text
non-mutating
ADMIN-authorized
zero DNS
zero provider HTTP
zero credential read/decryption
zero Tool/ToolRevision write
```

A nested edit invalidates any previous Response-validation success immediately, including edits that remain raw-local and cannot yet be promoted into the canonical definition.

## Publication / Preview Compatibility

### R21 — publication uses the same reconstruction compatibility rule

Update:

```text
src/commerce/tool-definition/publication.ts
```

so Visual publication compatibility accepts:

```text
legacy OBJECT
legacy LIST
new VISUAL
```

through the one canonical reconstruction helper.

Do not implement a second recursive publication compatibility algorithm.

Direct/JavaScript publication behavior remains unchanged.

### R22 — Studio sample/fixture processing must not diverge from runtime processing

The current Studio helper:

```text
src/studio/external-http/processor.ts
```

contains its own flat Visual projection implementation.

Do not create a second recursive algorithm there.

Refactor it to delegate/adapt to the same Commerce recursive response processor used by production, while retaining its Studio-facing `ExternalSampleResult` formatting/count metadata.

The synthetic fixture path remains local/sample processing only; this task does not add live provider I/O.

## Exact Files / Ownership

Expected primary implementation files:

```text
moda-interact-commerce/src/commerce/tool-definition/contracts.ts
moda-interact-commerce/src/commerce/tool-authoring/visual-result-contract.ts
moda-interact-commerce/src/commerce/external-response/index.ts
moda-interact-commerce/src/commerce/tool-authoring/external-validation.ts
moda-interact-commerce/src/commerce/tool-definition/publication.ts
moda-interact-commerce/src/studio/external-http/response-tab.tsx
moda-interact-commerce/src/studio/external-http/visual-tree-editor.tsx   # expected extraction; name may follow repository convention
moda-interact-commerce/src/studio/external-http/processor.ts
moda-interact-commerce/src/studio/external-http/ports.ts                 # only local type widening where required
moda-interact-commerce/app/styles.css                                    # nested visual presentation only
```

Expected focused tests:

```text
moda-interact-commerce/tests/visual-result-contract.test.ts
moda-interact-commerce/tests/response-processing.test.ts
moda-interact-commerce/tests/arch021-commerce-tool-contract.test.ts
moda-interact-commerce/tests/external-tool-authoring-validation.test.ts
moda-interact-commerce/tests/external-tool-authoring-server-actions.test.ts
moda-interact-commerce/tests/external-tools-ui.test.tsx
moda-interact-commerce/tests/tool-authoring-screen.test.tsx
moda-interact-commerce/tests/external-publication.test.ts
moda-interact-commerce/tests/external-preview.test.ts                    # when current fixture path is covered there
```

Do not modify unrelated services merely because they consume Tool definitions indirectly.

## Out of Scope

- Changes to `@modainteract/moda-interact-shared` or publishing a new Shared version.
- Prisma/database schema changes or data migrations.
- Live provider execution from the Response tab.
- Test-tab redesign or automatic schema inference from observed provider output.
- JavaScript response runtime changes.
- Request-tab changes.
- Agent-contract/template redesign.
- Review-tab redesign.
- Phase 2 navigation gating.
- Arbitrary expressions/functions in Visual mappings.
- Maps/dictionaries with dynamic output keys.
- Arrays of primitive scalars as a distinct Visual node type; LIST nodes in this task project rows into objects.
- Unbounded recursive nesting.

## Work Items

- [ ] Add Commerce-local recursive VISUAL processing schemas and types while retaining legacy Shared OBJECT/LIST parsing.
- [ ] Add exact recursive structural bounds and safe-path validation.
- [ ] Introduce one typed browser-local Visual authoring tree with array-backed raw fields and UI-only stable field IDs.
- [ ] Derive both canonical VISUAL processing and recursive resultSchema from the same authoring tree.
- [ ] Reconstruct authoring trees from both legacy flat and new recursive persisted definitions without guessing.
- [ ] Refactor production Visual processing to one recursive algorithm and adapt legacy flat processing through it.
- [ ] Implement nested OBJECT projection and nested LIST filter/sort/limit/projection semantics.
- [ ] Add the global 4096 inspected-row work budget plus existing cancellation/deadline checks.
- [ ] Extract recursive Visual UI from ResponseTab and add scalar/object/list field-type controls.
- [ ] Preserve per-field scalar/object/list drafts and root OBJECT/LIST drafts in browser-local state.
- [ ] Preserve invalid nested edits locally and prevent invalid active Visual state from Save/Create without gating navigation.
- [ ] Keep Visual processing/result-contract disclosures synchronized and truthful for valid/invalid local state.
- [ ] Extend Response-only validation to recursive VISUAL processing with deterministic nested issue paths.
- [ ] Route publication compatibility through the same recursive reconstruction helper.
- [ ] Refactor Studio synthetic Visual sample processing to delegate to the production recursive processor rather than duplicate it.
- [ ] Add focused backward-compatibility, nested-runtime, authoring, validation and publication regressions.

## Acceptance Criteria

- [ ] An OBJECT result can contain a nested LIST of projected objects without JavaScript.
- [ ] An OBJECT result can contain a nested OBJECT.
- [ ] A root LIST row can contain nested OBJECT and LIST fields.
- [ ] Nested OBJECT/LIST fields may themselves contain nested containers up to container depth 4.
- [ ] The canonical persisted recursive processing kind is exactly `VISUAL` and legacy OBJECT/LIST remain accepted/executable.
- [ ] New Visual authoring writes VISUAL processing; an untouched legacy persisted DRAFT is not rewritten merely by opening it.
- [ ] Persisted processing does not duplicate scalar result types; scalar types remain durable in derived `resultSchema`.
- [ ] One authoring-tree derivation produces processing and resultSchema together.
- [ ] Root LIST derives `{ items: [...] }`; nested LIST derives a raw array.
- [ ] Every object schema is closed with `additionalProperties:false` and requiredness exactly follows `omitIfMissing`.
- [ ] Compatible legacy and recursive definitions reconstruct deterministically; mismatches fail explicitly.
- [ ] Runtime nested paths are relative to the current parent/list-row source.
- [ ] Missing-path/omit semantics and wrong-shape failures follow R9 exactly.
- [ ] Every LIST applies filter -> stable sort -> limit -> recursive projection in that order.
- [ ] Structural limits (depth 4, 32 fields/container, 128 nodes, 8 filters/list, limit 20) are enforced before persistence/publication.
- [ ] Runtime enforces 1000 source rows per list and 4096 inspected rows across the full invocation.
- [ ] Cancellation/deadline remains bounded and a failed nested execution does not mutate source data.
- [ ] Final recursive output is still validated by the canonical `resultSchema` before Tool success.
- [ ] Response UI exposes string/integer/number/boolean/object/list Visual field types with nested editors.
- [ ] Nested list nodes have their own limit/sort/filter controls.
- [ ] Scalar/object/list branch drafts for a field survive switches during the authoring session and are never persisted when inactive.
- [ ] Root OBJECT/LIST drafts survive shape switches independently.
- [ ] Invalid nested values remain visible locally; Save/Create cannot persist an invalid active Visual tree; other tabs remain navigable.
- [ ] Processing/schema disclosures never present stale canonical JSON as the current invalid edit.
- [ ] Response-only validation produces deterministic nested issue paths and performs zero provider/credential/network/persistence I/O.
- [ ] Publication compatibility uses the shared Commerce reconstruction helper, not a second recursive validator.
- [ ] Studio synthetic sample processing uses the production recursive processor semantics rather than a duplicate recursive implementation.
- [ ] Direct and JavaScript response behavior is unchanged.
- [ ] Shared remains exactly 0.14.2; no Shared/Prisma migration is introduced.

## Mandatory Regression Scenarios

Add named tests that explicitly prove at least these cases.

### Contract derivation

```text
1. root OBJECT with nested LIST variants derives raw variants:[] array schema.
2. root LIST with nested OBJECT metadata derives {items:[...]} root envelope.
3. nested LIST maxItems equals its configured limit.
4. requiredness recursively follows omitIfMissing.
5. depth 5 is rejected.
6. >32 fields in one container is rejected.
7. >128 total projection nodes is rejected.
8. unsafe nested path segment (__proto__/prototype/constructor) is rejected.
```

### Reconstruction/backward compatibility

```text
9. legacy flat OBJECT reconstructs to scalar authoring nodes.
10. legacy flat LIST reconstructs with filters/sort/limit intact.
11. recursive VISUAL round-trips processing + resultSchema -> authoring -> same canonical processing/schema.
12. nested processing/schema structural mismatch is rejected, not guessed.
13. nested LIST persisted schema with maxItems >= limit is accepted; maxItems < limit is rejected.
```

### Runtime

```text
14. OBJECT -> nested LIST -> scalar children produces expected JSON.
15. OBJECT -> nested OBJECT -> scalar children produces expected JSON.
16. root LIST -> nested LIST produces {items:[{..., nested:[...]}]}.
17. nested LIST filter/sort/limit are evaluated against raw nested rows before projection.
18. missing required nested container -> INVALID_RESPONSE.
19. missing omitIfMissing nested container -> property omitted.
20. present nested container with wrong object/array type -> INVALID_RESPONSE even when omitIfMissing=true.
21. source objects are unchanged after processing.
22. 4096 inspected-row work budget fails closed; following ordinary processing still succeeds.
23. cancellation/deadline during deep/nested work returns the existing bounded cancellation/deadline result.
```

### UI / local state

```text
24. user authors OBJECT {title:string, variants:list{size:string, available:boolean}} and sees matching derived contract.
25. nested list controls expose their own filters/sort/limit.
26. duplicate/blank nested field names remain visible with errors and are not promoted canonically.
27. field LIST -> OBJECT -> LIST restores the prior LIST draft.
28. root OBJECT -> LIST -> OBJECT restores each root draft.
29. invalid nested edit immediately makes prior Response validation success stale.
30. invalid nested tree cannot Save/Create but Response/Test/Agent/Review tabs remain navigable.
31. legacy persisted flat Visual definition opens correctly without being rewritten solely by opening.
```

### Validation/publication

```text
32. Response-only validator accepts valid recursive VISUAL definition.
33. validator reports nested field/path/filter/limit issues at deterministic nested paths.
34. validator performs zero connection/credential/DNS/HTTP/Tool-write operations.
35. publication accepts compatible recursive tree/schema and rejects mismatched recursive tree/schema.
36. Direct and JavaScript validation/publication regressions remain green.
```

## Validation Commands

Inspect `package.json` first and use repository-declared scripts where available.

Run the current focused packets plus the new nested tests. At minimum:

```bash
npm run test:arch020-external-tools-ui
npm run test:arch021-external-tool-authoring-validation
npm run test:arch021-tool-authoring-common
```

Run focused files explicitly when no dedicated script owns them:

```bash
npx vitest run \
  tests/visual-result-contract.test.ts \
  tests/response-processing.test.ts \
  tests/arch021-commerce-tool-contract.test.ts \
  tests/external-tool-authoring-validation.test.ts \
  tests/external-tool-authoring-server-actions.test.ts \
  tests/external-tools-ui.test.tsx \
  tests/tool-authoring-screen.test.tsx \
  tests/external-publication.test.ts
```

If `tests/external-preview.test.ts` is changed, include it in the same focused run.

Run targeted lint over every changed source/test file and:

```bash
npm run typecheck
git diff --check
```

If repository-wide TypeScript remains non-zero only because of established unrelated baseline diagnostics, record the exact diagnostics/baseline reference and prove there is no diagnostic in a C048-modified file.

Run source audits:

```bash
# Shared version must remain exact and no workspace Shared change is allowed.
rg -n '"@modainteract/moda-interact-shared": "0\.14\.2"' package.json package-lock.json

# New canonical processing kind must exist in Commerce.
rg -n 'kind:\s*z\.literal\(["'"']VISUAL["'"']\)|kind:\s*["'"']VISUAL["'"']' src/commerce src/studio

# No persisted scalar type duplication inside canonical processing nodes.
! rg -n 'resultType' src/commerce/tool-definition
```

Inspect the final diff to confirm no files under:

```text
moda-interact-shared/
moda-interact-database/
```

were modified.

## Stop Condition

After recursive Visual processing, derivation/reconstruction, runtime execution, Response validation, publication compatibility, recursive UI authoring and the mandatory regressions above are complete, set this task to `review`, complete the Completion Report and STOP.

Do not continue into live Test-tab provider execution, Direct/JavaScript sample schema inference, Agent-contract redesign, Review redesign, database work or Shared publication.

## Implementation Notes

This task intentionally introduces `kind:"VISUAL"` rather than changing the grammar of the Shared legacy OBJECT/LIST schema. That makes backward compatibility explicit and keeps Shared pinned at 0.14.2.

Prefer small composable functions over recursive logic embedded in React event handlers. In particular, keep these concerns separate:

```text
raw UI tree
  -> derive/canonicalise
  -> persisted VISUAL processing + resultSchema

persisted processing + resultSchema
  -> reconstruct UI tree

runtime source + canonical processing
  -> recursive projected value
```

The runtime and Studio fixture path must share execution semantics. The UI and publication validator must share derivation/reconstruction semantics.

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
