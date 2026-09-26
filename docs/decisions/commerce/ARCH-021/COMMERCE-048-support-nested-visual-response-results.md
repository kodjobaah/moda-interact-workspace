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
status: review
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

Extend External HTTP Visual response authoring from the current flat scalar projection model to one bounded recursive Commerce-owned Visual tree that can produce nested objects and nested lists without requiring JavaScript.

The first-class example is:

```json
{
  "title": "T-Shirt",
  "price": 20,
  "variants": [
    { "size": "S", "available": true },
    { "size": "M", "available": false }
  ]
}
```

The implementation must also remove the accidental architectural dependency whereby Commerce output/result schemas are constrained by Shared `DetailsSchemaSchema` even though this result contract does not cross an application-domain boundary.

## Context

ARCH-021 already made the full Tool definition Commerce-owned. The cross-service Tool descriptor contains only:

```text
name
description
inputSchema
```

It does not expose:

```text
execution
responseProcessing
resultSchema
connectionRevisionId
request/response JavaScript
provider configuration
```

Therefore `resultSchema` is a Commerce-local execution/result contract. Reusing Shared `DetailsSchemaSchema` and `compileSubset(..., "details")` is implementation reuse, not contract ownership.

The current accepted flat Visual model supports only:

```text
root OBJECT -> scalar projected fields
root LIST   -> scalar projected row fields -> { items: [...] }
```

and cannot express nested containers.

Implementation investigation also proved that Shared 0.14.2's Details-schema depth restriction would unnecessarily constrain nested Commerce-only results. C048 must remove that coupling rather than make Shared authoritative for a Commerce-local contract.

The product is preproduction. No backward-compatibility layer is required for old development-only Visual processing shapes or persisted development fixtures.

## Architectural Decisions

### AD1 — Commerce owns `resultSchema`

Create a Commerce-local canonical result-schema contract under:

```text
src/commerce/tool-definition/result-schema.ts
```

Export at minimum:

```ts
CommerceResultSchemaSchema
CommerceResultSchema
compileCommerceResultSchema(...)
```

Equivalent internal helper names are acceptable only if there is still one obvious canonical Commerce result-schema parser/type/compiler boundary.

`CommerceResultSchemaSchema` becomes authoritative for Commerce result schemas, including:

```text
EXTERNAL_HTTP.resultSchema
SHOPIFY_ADMIN_GRAPHQL.resultSchema
publication/template output-schema composition
External HTTP runtime result validation
External fixture/sample validation
Response-authoring validation
Visual schema derivation/reconstruction
```

Do not parse a Commerce `resultSchema` through Shared `DetailsSchemaSchema` after this task.

Do not use Shared `compileSubset(schema, "details")` to validate Commerce execution output after this task.

Shared remains authoritative only for genuinely shared contracts/utilities still crossing service boundaries, including `InputSchemaSchema` and the Shared Tool descriptor.

### AD2 — Shared remains pinned but is not authoritative for Commerce result schemas

Keep the package dependency unchanged:

```json
"@modainteract/moda-interact-shared": "0.14.2"
```

Do not edit or publish `moda-interact-shared` for this task.

Shared helpers such as `safeName`, `safePath`, canonical JSON helpers, IDs and input-schema compilation may still be reused where appropriate. Their reuse must not make a Commerce-local result contract subject to unrelated Shared schema limits.

### AD3 — one canonical preproduction Visual grammar

After C048, canonical Commerce response processing is exactly:

```text
DIRECT
VISUAL
JAVASCRIPT
```

The old flat canonical Visual processing kinds:

```text
OBJECT
LIST
```

must be removed from the Commerce-local canonical response-processing union.

Do not retain:

```text
legacy OBJECT/LIST parser branch
legacy runtime adapter
migration-on-read
open-old-and-rewrite behavior
published-definition compatibility shim
```

because the system is preproduction.

Update test fixtures, seed/development definitions and local examples to `kind:"VISUAL"`. If an existing development database contains old definitions, reset/reseed is acceptable and should be documented rather than adding compatibility code.

### AD4 — exact persisted Visual processing representation

Use exactly one persisted root discriminator:

```ts
kind: "VISUAL"
```

Root OBJECT:

```ts
{
  kind: "VISUAL";
  shape: "OBJECT";
  fields: Record<string, VisualProjectionNode>;
}
```

Root LIST:

```ts
{
  kind: "VISUAL";
  shape: "LIST";
  fields: Record<string, VisualProjectionNode>;
  filters: VisualFilter[];
  sort: VisualSort | null;
  limit: number;
}
```

Nested nodes are:

```ts
type VisualScalarProjection = {
  kind: "SCALAR";
  path: string;
  omitIfMissing?: true;
};

type VisualObjectProjection = {
  kind: "OBJECT";
  path: string;
  fields: Record<string, VisualProjectionNode>;
  omitIfMissing?: true;
};

type VisualListProjection = {
  kind: "LIST";
  path: string;
  fields: Record<string, VisualProjectionNode>;
  filters: VisualFilter[];
  sort: VisualSort | null;
  limit: number;
  omitIfMissing?: true;
};
```

Scalar result types are not duplicated into `responseProcessing`; they remain durable in the derived Commerce `resultSchema`.

### AD5 — Visual container depth remains four

The Visual authoring/runtime structural bound is:

```text
maximum container depth:        4
maximum fields per container:   32
maximum total projection nodes: 128
maximum filters per LIST:       8
maximum configured LIST limit:  20
```

Depth is defined only by Visual OBJECT/LIST containers:

```text
root OBJECT/LIST container = depth 1
nested OBJECT/LIST         = parent depth + 1
SCALAR leaves              = do not add container depth
```

Therefore this is valid:

```text
root OBJECT                 depth 1
  product OBJECT            depth 2
    variants LIST           depth 3
      option OBJECT         depth 4
        name SCALAR
```

A container below `option` would be rejected as depth 5.

The Commerce result-schema validator must be capable of representing every result schema derivable from a valid depth-4 Visual tree. Do not reintroduce a shallower schema-depth limit that makes a valid Visual tree impossible to persist.

## Commerce Result Schema Contract

### R1 — exact supported schema subset

`CommerceResultSchemaSchema` must support exactly the result/output subset required by current Commerce execution:

```text
string
integer
number
boolean
object
array
```

Supported scalar forms:

```ts
{ type: "string", maxLength: integer 1..4096 }
{ type: "integer" }
{ type: "number" }
{ type: "boolean" }
```

Supported object form:

```ts
{
  type: "object";
  properties: Record<safeName, CommerceResultSchema>;
  required: string[];
  additionalProperties: false;
}
```

Rules:

```text
1..32 properties
required is unique
required contains only keys present in properties
no unknown schema keywords
additionalProperties must be exactly false
```

Supported array form:

```ts
{
  type: "array";
  items: CommerceResultSchema;
  maxItems: integer 1..20;
}
```

Do not add:

```text
oneOf / anyOf / allOf
$ref
patternProperties
additionalProperties schemas
regex validation
nullable unions
arbitrary enum/const
unbounded arrays/strings
```

unless another architecture task explicitly adds them.

### R2 — result-schema resource bounds

The Commerce result-schema parser/compiler must reject before unbounded recursion or validation work.

Use these independent schema bounds:

```text
maximum schema depth:          12
maximum schema nodes:          256
maximum object properties:      32 per object
maximum array maxItems:         20
maximum string maxLength:     4096
```

Schema depth counts schema nodes and is separate from Visual container depth. `12` is intentionally large enough for every result schema produced by a four-container Visual tree including root-LIST envelope/array/row-object expansion.

A Visual tree must first satisfy the Visual depth/node limits and then its derived schema must satisfy the Commerce result-schema bounds.

### R3 — one Commerce result compiler

Implement `compileCommerceResultSchema(schema)` as the only production output validator for Commerce result values.

The compiler must:

```text
parse/accept only CommerceResultSchemaSchema
validate runtime values recursively
reject unknown object keys
require every required property
validate scalar types exactly
require finite numbers
respect maxLength using JavaScript string length semantics already used by the schema contract
respect maxItems
return deterministic bounded issue paths/messages
never mutate input values
```

A production call site must not compile equivalent result-schema logic independently.

Input validation remains separate:

```text
Shared InputSchemaSchema + compileSubset(..., "input")
```

Do not replace the Shared input contract in C048.

### R4 — replace every Commerce details-schema dependency in result/output paths

At minimum inspect and update these current call sites:

```text
src/commerce/tool-definition/contracts.ts
src/commerce/tool-definition/publication.ts
src/commerce/tool-authoring/visual-result-contract.ts
src/commerce/tool-authoring/external-validation.ts
src/commerce/external-http/index.ts
src/commerce/external-preview/fixture-runner.ts
src/commerce/external-publication/index.ts
src/studio/external-http/ports.ts
```

Also run repository search and update any additional production/test result-schema consumer discovered by:

```bash
rg -n 'DetailsSchemaSchema|compileSubset\([^\n]*["'"']details["'"']|resultSchema' src tests
```

After C048, no Commerce production result/output path may depend on Shared `DetailsSchemaSchema` or Shared `compileSubset(..., "details")`.

Shopify Admin result schemas should use the same Commerce result-schema contract so Commerce has one output-schema language.

## Recursive Visual Contract

### R5 — exact recursive local Zod schema

Implement the recursive processing schema in:

```text
src/commerce/tool-definition/contracts.ts
```

or a single adjacent Commerce-local module imported by it.

Use `z.lazy(...)` where appropriate and preserve these rules:

```text
output names: safeName
source/filter/sort paths: safe dot paths
forbidden path segments:
  __proto__
  prototype
  constructor
fields/container: 1..32
filters/list: 0..8
list limit: 1..20
sort direction: ASC | DESC
```

Filter operators remain exactly:

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

Filter scalar values remain:

```text
string
finite number
boolean
null
```

`IN` remains 1..20 values of one scalar type.

Do not introduce predicates, expressions, regex or JavaScript into Visual filters.

### R6 — one browser-local typed authoring tree

The browser-local authoring tree must carry the scalar result type because persisted processing does not:

```ts
type VisualAuthoringScalarNode = {
  kind: "SCALAR";
  path: string;
  resultType: "string" | "integer" | "number" | "boolean";
  omitIfMissing?: true;
};
```

OBJECT/LIST authoring nodes mirror the persisted structure and contain array-backed child fields with a browser-only stable `clientId`.

Use arrays for raw field authoring so the UI can retain invalid intermediate states including:

```text
blank output name
duplicate output name
invalid output name
missing type
invalid source path
incomplete OBJECT/LIST
invalid limit/filter/sort
```

`clientId` must never be persisted.

### R7 — derive processing and result schema together

There must be one canonical helper equivalent to:

```ts
deriveVisualContract(authoringTree)
  -> {
       processing: VisualTreeResponseProcessing;
       resultSchema: CommerceResultSchema;
     }
```

The derivation order is:

```text
1. validate raw authoring names/paths/types/container configuration
2. enforce Visual depth/field/node/filter/list limits
3. build canonical kind:"VISUAL" processing
4. derive the complete Commerce resultSchema from the exact same tree
5. parse the derived schema through CommerceResultSchemaSchema
6. return both artifacts together
```

Do not derive processing and schema in different UI handlers.

### R8 — exact recursive result-schema mapping

SCALAR mapping:

```text
string  -> { type:"string", maxLength:4096 }
integer -> { type:"integer" }
number  -> { type:"number" }
boolean -> { type:"boolean" }
```

OBJECT node mapping:

```text
type: object
properties: exactly authored child output names
required: exactly children without omitIfMissing
additionalProperties: false
```

Nested LIST node mapping:

```text
type: array
items:
  closed object schema for the projected row
maxItems: exact configured list limit
```

Root LIST remains the product-level envelope:

```text
{
  type: "object",
  properties: {
    items: {
      type: "array",
      items: <closed projected-row object>,
      maxItems: <root list limit>
    }
  },
  required: ["items"],
  additionalProperties: false
}
```

Therefore:

```text
root LIST   -> { items: [...] }
nested LIST -> [...]
```

### R9 — reconstruction is only for the new canonical format

Provide one helper equivalent to:

```ts
reconstructVisualAuthoringTree(processing, resultSchema)
```

It only needs to support:

```text
kind:"VISUAL" + CommerceResultSchema
```

It must reconstruct scalar `resultType` values and verify processing/schema structural agreement recursively.

Reject instead of guessing on:

```text
processing field missing from schema
schema field missing from processing
required/omitIfMissing mismatch
OBJECT paired with non-object schema
LIST paired with non-array schema
root LIST missing {items:[...]} envelope
unsupported scalar type
string without valid maxLength
maxItems < configured list limit
unsafe path
unexpected schema property
```

Do not add legacy flat OBJECT/LIST reconstruction in this task.

## Runtime Processing

### R10 — one recursive Visual processor

Update:

```text
src/commerce/external-response/index.ts
```

so `VISUAL` processing runs through one canonical recursive projector.

There is no legacy flat Visual runtime adapter after C048.

DIRECT and JAVASCRIPT remain unchanged.

### R11 — relative-path semantics

`execution.resultPath` selects the root JSON value before Visual processing.

Inside the Visual tree all paths are relative to the current node source:

```text
SCALAR.path
OBJECT.path
LIST.path
filter.path
sort.path
```

Example:

```text
root source
  product.title
  product.variants[]

root OBJECT
  title SCALAR path=product.title
  variants LIST path=product.variants
    size SCALAR path=size
    available SCALAR path=available
```

### R12 — missing/wrong-shape semantics

For every SCALAR/OBJECT/LIST field:

```text
missing path + omitIfMissing=true  -> omit output field
missing path + required            -> INVALID_RESPONSE
present OBJECT with non-object     -> INVALID_RESPONSE
present LIST with non-array        -> INVALID_RESPONSE
present SCALAR object/array        -> INVALID_RESPONSE
```

`omitIfMissing` applies only to a missing path; it does not forgive a present wrong-shaped value.

### R13 — nested LIST operation order

Every root or nested LIST performs:

```text
resolve source array
  -> enforce source-row bound
  -> filters
  -> stable sort
  -> limit
  -> recursively project selected rows
```

Filters/sort operate on raw list rows before projection.

### R14 — runtime work bounds

Preserve/add:

```text
maximum source rows inspected per LIST: 1000
maximum inspected LIST rows per invocation: 4096
maximum Visual container depth: 4
maximum projection nodes: 128
existing cancellation/deadline checks
```

Exceeding a bound must fail closed through the existing bounded processor error/result model and must not mutate source data.

### R15 — final Commerce result validation remains mandatory

Every successful Visual/Direct/JavaScript External HTTP result must be validated through:

```ts
compileCommerceResultSchema(execution.resultSchema).safeParse(processed.values)
```

before returning Tool success.

The same compiler must be used by fixture/sample processing where the saved `resultSchema` is validated.

## Studio / Response UI

### R16 — extract a recursive Visual editor

Do not grow `response-tab.tsx` into one recursive monolith.

Create/reuse a component such as:

```text
src/studio/external-http/visual-tree-editor.tsx
```

with recursive field rendering.

`response-tab.tsx` remains responsible for mode/root coordination and delegates nested Visual tree editing.

### R17 — exact field type choices

Each projected field exposes:

```text
string
integer
number
boolean
object
list
```

Selecting:

```text
string/integer/number/boolean -> SCALAR branch
object                        -> OBJECT branch
list                          -> LIST branch
```

New OBJECT/LIST branches receive deterministic minimal local defaults but are not promoted canonically until valid.

### R18 — preserve branch drafts

For each browser-local field, retain independent SCALAR/OBJECT/LIST branch drafts keyed by stable `clientId`.

Example:

```text
field LIST -> OBJECT -> LIST
```

restores the previous LIST configuration including nested fields/filter/sort/limit.

Root OBJECT and root LIST drafts must remain independent as established by C045.

Inactive drafts are browser-only and never persisted.

### R19 — invalid edits remain visible

Invalid nested edits must:

```text
remain visible
show local actionable errors
immediately invalidate prior Response-validation success
not overwrite the last valid canonical definition
prevent Save/Create of the invalid active tree
not gate navigation to Request/Test/Agent/Review
```

### R20 — disclosures describe current local truth

For a valid current Visual tree:

```text
View Visual processing JSON
  -> current canonical kind:"VISUAL" processing

Derived result contract
  -> current Commerce resultSchema
```

For an invalid current tree, do not display stale old canonical JSON/schema as if it represents the current edits. Mark the disclosure invalid/unavailable until the local tree is valid again.

### R21 — Response-only validation supports VISUAL

Extend COMMERCE-044's authoritative Response validator to validate:

```text
DIRECT
VISUAL
JAVASCRIPT
```

Visual validation must use the same derive/reconstruct helpers and return deterministic nested issue paths.

It must still perform zero:

```text
DNS
provider HTTP
credential reads/decryption
Tool/ToolRevision writes
```

## Publication / Preview

### R22 — publication compatibility uses the canonical Commerce helpers

Publication must validate recursive Visual processing/result-schema compatibility via the same Commerce reconstruction/derivation semantics.

Do not maintain a second recursive compatibility algorithm.

Template path traversal must understand the Commerce result-schema structure without importing Shared `SubsetSchema` as the authoritative result type.

### R23 — Studio synthetic/fixture processing reuses production Visual semantics

Any Studio sample/synthetic Visual processing path must delegate to the production recursive Visual processor or a shared Commerce execution helper.

Do not create another recursive projector in Studio.

## Preproduction Migration Rule

### R24 — no backward-compatibility implementation

Because the system is preproduction:

```text
old flat OBJECT/LIST persisted definitions are not supported after C048
old development fixtures/seeds are updated in source
no runtime compatibility adapter is required
no migration-on-read is required
no DB migration script is required
no old/new dual parser is required
```

If local development data contains old definitions, document the required reset/reseed command or manual development reset procedure already used by the repository.

Do not add production migration complexity to preserve development-only state.

## Exact Files / Ownership

Expected implementation ownership includes at minimum:

```text
src/commerce/tool-definition/result-schema.ts              NEW
src/commerce/tool-definition/contracts.ts
src/commerce/tool-definition/publication.ts
src/commerce/tool-authoring/visual-result-contract.ts
src/commerce/tool-authoring/external-validation.ts
src/commerce/external-response/index.ts
src/commerce/external-http/index.ts
src/commerce/external-preview/fixture-runner.ts
src/commerce/external-publication/index.ts
src/studio/external-http/response-tab.tsx
src/studio/external-http/visual-tree-editor.tsx             NEW or equivalent focused component
src/studio/external-http/ports.ts
```

Update focused tests/fixtures/seeds wherever repository search proves ownership.

Do not modify another repository for C048.

## Out of Scope

- Editing/publishing `moda-interact-shared`.
- Database/Prisma schema migration.
- Production backward-compatibility or migration for old Visual definitions.
- Live provider execution in Test.
- Direct/JavaScript sample-derived schema inference.
- Arrays of primitive values as a dedicated Visual LIST node; LIST projects row objects.
- Dynamic-map/object keys.
- Arbitrary Visual expressions/JavaScript.
- Unbounded recursion.
- Phase 2 navigation gating.

## Work Items

- [x] Add `CommerceResultSchemaSchema`, `CommerceResultSchema` and one Commerce result compiler.
- [x] Replace Shared Details-schema parsing/compilation on Commerce result/output paths.
- [x] Keep Shared input-schema/Tool-descriptor boundaries unchanged.
- [x] Make canonical Response processing exactly DIRECT | VISUAL | JAVASCRIPT.
- [x] Remove legacy flat OBJECT/LIST compatibility branches and update development fixtures/seeds.
- [x] Enforce recursive VISUAL structural/path/filter bounds.
- [x] Introduce one array-backed browser-local recursive authoring tree with stable UI-only IDs.
- [x] Derive canonical VISUAL processing and Commerce resultSchema together.
- [x] Reconstruct the authoring tree from canonical VISUAL + Commerce resultSchema only.
- [x] Implement one production recursive Visual projector.
- [x] Implement nested OBJECT and LIST semantics including per-list filter/sort/limit.
- [x] Enforce runtime source-row/global inspected-row budgets and cancellation/deadline checks.
- [x] Extract recursive UI into a focused component and preserve branch/root drafts.
- [x] Preserve invalid nested edits locally and prevent invalid Save/Create without tab gating.
- [x] Keep processing/schema disclosures synchronized with current local validity.
- [x] Extend Response-only validation to canonical VISUAL.
- [x] Route publication compatibility through the same Commerce reconstruction helper.
- [x] Route fixture/sample result validation through the Commerce result compiler.
- [x] Route synthetic Visual processing through production recursive semantics.
- [x] Add explicit preproduction reset/reseed note where current development data needs replacement.

## Acceptance Criteria

- [x] Commerce, not Shared, owns the canonical result-schema parser/type/compiler.
- [x] No Commerce production result/output path imports Shared `DetailsSchemaSchema` or calls Shared `compileSubset(..., "details")`.
- [x] Shared `InputSchemaSchema` / `compileSubset(..., "input")` and Shared Tool descriptor remain unchanged.
- [x] `CommerceResultSchemaSchema` supports bounded nested object/array/scalar output with schema depth 12 and node bound 256.
- [x] Canonical response processing is exactly DIRECT | VISUAL | JAVASCRIPT.
- [x] No legacy flat OBJECT/LIST runtime/parser/reconstruction branch remains.
- [x] An OBJECT result can contain a nested LIST of projected objects without JavaScript.
- [x] An OBJECT result can contain a nested OBJECT.
- [x] A root LIST row can contain nested OBJECT/LIST fields.
- [x] Nested containers are supported through Visual container depth 4.
- [x] Processing does not duplicate scalar result types; result types remain in derived Commerce resultSchema.
- [x] One derivation produces processing and resultSchema together.
- [x] Root LIST derives `{items:[...]}`; nested LIST derives a raw array.
- [x] All object schemas are closed and requiredness follows `omitIfMissing`.
- [x] Canonical VISUAL + Commerce resultSchema reconstruct deterministically; mismatches fail explicitly.
- [x] Runtime paths are relative to the current source/list row.
- [x] Missing/wrong-shape semantics follow R12 exactly.
- [x] Every LIST applies filter -> stable sort -> limit -> recursive projection.
- [x] Structural/runtime work limits are enforced before runaway work.
- [x] Final output is validated by `compileCommerceResultSchema` before Tool success.
- [x] Response UI exposes scalar/object/list nested editing and preserves inactive branch drafts.
- [x] Invalid nested values remain visible locally and cannot be saved/created while invalid.
- [x] Validation success becomes stale on every relevant local edit.
- [x] Response-only validation performs zero provider/credential/network/persistence I/O.
- [x] Publication and fixture/sample paths use the canonical Commerce schema/Visual helpers.
- [x] Direct and JavaScript behavior remains unchanged apart from using Commerce result-schema validation.
- [x] Shopify Admin resultSchema continues to parse/validate under the new Commerce result-schema contract.
- [x] No Shared/Prisma publication or migration is introduced.

## Mandatory Regression Scenarios

### Commerce result schema

```text
1. nested object/array result schema beyond Shared Details depth 4 parses through CommerceResultSchemaSchema.
2. schema depth >12 is rejected.
3. schema node count >256 is rejected.
4. object with unknown property is rejected by compiled runtime validation.
5. missing required property is rejected with deterministic path.
6. array above maxItems is rejected.
7. string above maxLength is rejected.
8. non-finite number is rejected.
9. unsupported schema keyword is rejected.
10. Shopify Admin flat result schema remains accepted by CommerceResultSchemaSchema.
```

### Visual derivation

```text
11. root OBJECT with nested LIST variants derives raw variants:[] array schema.
12. root LIST with nested OBJECT/list descendants derives the root {items:[...]} envelope.
13. nested LIST maxItems exactly equals configured limit.
14. requiredness recursively follows omitIfMissing.
15. valid Visual container depth 4 derives a valid Commerce result schema.
16. Visual container depth 5 is rejected before canonical persistence.
17. >32 fields/container is rejected.
18. >128 projection nodes is rejected.
19. unsafe nested path segment (__proto__/prototype/constructor) is rejected.
20. VISUAL + resultSchema round-trips through reconstruction to the same canonical pair.
21. structural processing/schema mismatch is rejected, not guessed.
```

### Runtime

```text
22. OBJECT -> nested LIST -> scalar children produces expected JSON.
23. OBJECT -> nested OBJECT -> scalar children produces expected JSON.
24. root LIST -> nested LIST/OBJECT descendants produces {items:[...]} correctly.
25. nested LIST filter/sort/limit operates on raw nested rows before projection.
26. missing required nested container -> INVALID_RESPONSE.
27. missing omitIfMissing nested container -> output property omitted.
28. present nested container with wrong type -> INVALID_RESPONSE even when optional.
29. source objects remain unchanged after processing.
30. 4096 inspected-row budget fails closed and following ordinary processing still succeeds.
31. cancellation/deadline during nested work returns the existing bounded failure result.
32. successful processed output is rejected when it violates Commerce resultSchema.
```

### UI/local state

```text
33. user authors OBJECT {title:string, variants:list{size:string, available:boolean}} and sees matching derived contract.
34. nested list exposes its own filters/sort/limit controls.
35. blank/duplicate nested names remain visible with local errors and are not promoted.
36. field LIST -> OBJECT -> LIST restores prior LIST draft.
37. field SCALAR -> LIST -> SCALAR restores prior scalar path/type draft.
38. root OBJECT -> LIST -> OBJECT restores independent root drafts.
39. invalid nested edit immediately invalidates prior Response-validation success.
40. invalid active tree cannot Save/Create but all authoring tabs remain navigable.
41. processing/result disclosures never show stale canonical JSON as current invalid state.
```

### Preproduction/canonical grammar

```text
42. LocalResponseProcessingSchema rejects old flat kind:"OBJECT".
43. LocalResponseProcessingSchema rejects old flat kind:"LIST".
44. canonical new Visual fixtures/seeds use kind:"VISUAL".
45. no production legacy Visual adapter/reconstruction branch remains by source audit.
```

### Validation/publication

```text
46. Response-only validator accepts valid recursive VISUAL definition.
47. validator reports nested field/path/filter/limit issues at deterministic nested paths.
48. validator performs zero connection/credential/DNS/HTTP/Tool-write operations.
49. publication accepts compatible recursive Visual processing/schema and rejects mismatch.
50. External HTTP fixture validation uses compileCommerceResultSchema.
51. External HTTP runtime uses compileCommerceResultSchema.
52. Direct/JavaScript validation/publication regressions remain green.
53. Shopify Admin contract regression remains green under CommerceResultSchemaSchema.
```

## Validation Commands

Inspect `package.json` and use existing repository scripts where available. At minimum run the focused equivalents of:

```bash
npm run test:arch021-commerce-tool-contract
npm run test:arch021-external-tool-authoring-validation
npm run test:arch020-code-processor
npm run test:arch021-external-tool-ui
```

Run the exact focused Visual/result/runtime/UI tests added or modified by C048.

Then run:

```bash
npm run typecheck
npm run lint
git diff --check
```

Repository-wide baseline failures may be recorded only when unchanged and unrelated; there must be zero C048-owned diagnostics.

Run these required source audits:

```bash
# Shared must remain pinned and unmodified.
git diff --exit-code -- moda-interact-shared

# No Shared Details-schema authority in Commerce result/output paths.
! rg -n 'DetailsSchemaSchema' src/commerce src/studio
! rg -n 'compileSubset\([^\n]*["'"']details["'"']' src/commerce src/studio

# Shared input contract remains in use.
rg -n 'InputSchemaSchema|compileSubset\([^\n]*["'"']input["'"']' src/commerce

# One canonical Visual discriminator.
rg -n 'kind:\s*z\.literal\(["'"']VISUAL["'"']\)|kind:\s*["'"']VISUAL["'"']' src/commerce src/studio

# No canonical legacy flat Visual processing discriminator remains.
! rg -n 'responseProcessing[^\n]*(OBJECT|LIST)|kind:\s*z\.literal\(["'"'](OBJECT|LIST)["'"']\)' src/commerce/tool-definition src/commerce/external-response src/commerce/tool-authoring src/studio/external-http
```

The last audit may exclude unrelated object/list schema terminology; its purpose is to prove no legacy flat response-processing discriminator remains.

## Stop Condition

When Commerce owns the result-schema parser/compiler, the canonical response-processing union is DIRECT | VISUAL | JAVASCRIPT only, nested Visual execution/UI/validation/publication/fixture semantics are implemented through the canonical helpers, all required focused regressions pass, and validation/source audits are reconciled, set the task to `review`, complete the Completion Report and STOP.

Do not continue into live Test provider execution, Direct/JavaScript sample schema inference, Agent-contract redesign, Review redesign, database work or Shared publication.

## Implementation Notes

Preserve the current in-progress C048 implementation work where it conforms to this revised architecture. The task remains Attempt 1; do not restart merely because the ownership contract changed during implementation.

Preferred dependency direction:

```text
raw UI Visual tree
  -> deriveVisualContract
       -> canonical VISUAL processing
       -> CommerceResultSchema

canonical VISUAL processing + CommerceResultSchema
  -> reconstruct UI tree

runtime source + VISUAL processing
  -> recursive projected value
  -> compileCommerceResultSchema(resultSchema)

Tool descriptor boundary
  -> Shared name/description/inputSchema only
```

Do not introduce a second result-schema compiler in Studio or publication code.

## Completion Report

### Status
Ready for architect review

### Execution Isolation
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-048`, `task/ARCH-021-COMMERCE-048`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-048`, `task/ARCH-021-COMMERCE-048`.
- Shared workspace and source checkouts were not switched or modified for implementation; no other task worktree was reused.
- The parent task branch was synchronized to `origin/task/ARCH-021-COMMERCE-048` at the revised task-definition commit `c62057ca`. The implementation branch started at `origin/main` commit `b6f3f0f`; no remote implementation task ref existed before this attempt, so the task branch will be published as a new remote ref.
- Prepared recursive submodule synchronization/update passed. The recorded implementation submodule is `database` at `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.

### Files Changed
Commerce result schema/contracts, recursive Visual derivation and reconstruction, External HTTP runtime/preview/publication/fixture validation, Studio synthetic processing and recursive response UI, the new External HTTP starter definition, and focused Commerce tests/fixtures. No Shared, database, or Prisma files changed.

### Work Completed
- Added the Commerce-owned bounded result-schema parser/compiler (depth 12, 256 schema nodes) and moved Commerce output validation to it while retaining Shared input-schema validation.
- Replaced flat root OBJECT/LIST response-processing kinds with the canonical DIRECT | VISUAL | JAVASCRIPT union; nested Visual OBJECT/LIST nodes use one recursive contract, projector, derivation/reconstruction path, and publication compatibility check.
- Added recursive Visual authoring with local validation, synchronized current-validity disclosures, independent root shape drafts, and per-field SCALAR/OBJECT/LIST branch retention keyed by browser-only client IDs.
- Routed runtime, fixture/sample validation, publication, and Studio synthetic processing through the Commerce-owned schema/Visual helpers; updated old development fixtures and the starter tool.
- Documented the preproduction data rule: local definitions using the removed flat modes must be discarded and recreated through Studio, or the disposable local development database reset/reseeded using the repository's local procedure. No migration or compatibility adapter was added.

### Validation Results
- `npm run test:arch021-commerce-tool-contract`: 16 passed.
- `npm run test:arch021-external-tool-authoring-validation`: 47 passed.
- `npm run test:arch020-code-processor`: 6 passed.
- `npm run test:arch020-external-tools-ui`: 33 passed, including nested branch-draft retention. The task's suggested `test:arch021-external-tool-ui` name is not declared in this repository; the existing focused UI script was used.
- Focused C048 contract, schema, runtime, authoring, UI, execution, preview, and publication batch: 182 passed across 12 test files.
- `npm run lint`: 0 errors, 7 warnings (existing warnings in unrelated source/tests and an existing unused test import).
- `npm run typecheck`: blocked by the existing repository-wide baseline of 251 diagnostics across 22 files. The diagnostics are in unrelated Prisma-backed areas or pre-existing portions of fixture/test files; none are on C048-edited lines or in C048-owned implementation code.
- `git diff --check`: passed. Source audits confirmed Shared remains pinned at 0.14.2 and unchanged; no Commerce/Studio `DetailsSchemaSchema` or details-mode compiler use remains; Shared compilation is input-only; root processing is Direct/Visual/JavaScript, with OBJECT/LIST only as nested Visual nodes.

### Deviations
- The task's suggested C048-specific UI npm script is absent from `package.json`; ran the existing `test:arch020-external-tools-ui` script instead.
- Whole-repository typecheck remains non-green because of the documented unrelated baseline diagnostics; focused behavior tests and lint pass.

### Assumptions
Old flat Visual definitions are development-only state and need local recreation; no production compatibility or data migration is required. Reset only a disposable local development database if manual recreation is not sufficient.

### Unresolved Issues
None within C048 scope. Architect review is pending.

### Architectural Concerns
None. Shared remains at 0.14.2 and no Shared or Prisma changes were introduced.

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
