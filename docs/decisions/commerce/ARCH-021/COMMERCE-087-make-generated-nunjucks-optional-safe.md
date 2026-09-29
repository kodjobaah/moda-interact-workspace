---
id: ARCH-021-COMMERCE-087
architecture_id: ARCH-021
title: Make generated Nunjucks templates total over optional result fields
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 74
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-084
enables: []
created: 2026-09-29
updated: 2026-09-29
---

# Make generated Nunjucks templates total over optional result fields

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Make the `nunjucks.v1` default-template generator and canonical Result Template validator safe for schema-permitted omitted result properties, so **every generator-produced Result Template renders successfully for every `CommerceToolResult` value accepted by the canonical Response/result contract, unless rendering fails for a reason other than a schema-permitted omitted optional value**.

This task fixes the generator/validator/runtime contract. It does **not** redesign the Result Template editor.

## Context

The current generated template for a Response whose projected item fields are configured as `Omit if missing` can contain unconditional dereferences such as:

```nunjucks
Items:
{% for item in result.values.items %}
  Department: {{ item.department }}
  Description: {{ item.description }}
  Id: {{ item.id }}
  Image: {{ item.image }}
  Name: {{ item.name }}
  Price: {{ item.price }}
{% else %}
  No items available.
{% endfor %}
```

The Response/result contract may validly accept an item such as:

```json
{
  "name": "Widget",
  "price": "12.99"
}
```

while omitting:

```text
department
description
id
image
```

A Result Template generated from that contract must not pass authoring validation and then fail at `resultRendering` merely because those optional properties are absent.

The observed live-Test sequence motivating this correction is:

```text
requestConstruction   Passed
connectionResolution Passed
providerRequest       Passed
responseProcessing    Passed
resultValidation      Passed
resultRendering       Failed
```

with stable Test failure code:

```text
RESULT_RENDERING_FAILED
```

This task must prove the root cause from source/tests rather than assuming every `RESULT_RENDERING_FAILED` is an optional-property problem. If the reproduced failure is not caused by schema-permitted omission, record that evidence and return the task Blocked to `moda_architect` before changing unrelated rendering semantics.

## Scope

Primary Commerce implementation areas, using the actual C084 locations if names differ mechanically:

```text
moda-interact-commerce/src/commerce/tool-authoring/result-template-generator.ts
moda-interact-commerce/src/commerce/tool-authoring/result-template-contract.ts
moda-interact-commerce/src/commerce/tool-authoring/nunjucks-template.ts
moda-interact-commerce/src/commerce/execution/renderer.ts
```

Canonical validation/publication/Test callers may be changed only where required to consume the corrected canonical validator; do not duplicate optional-path logic in those callers.

Focused tests include, as applicable:

```text
moda-interact-commerce/tests/result-template-authoring.test.ts
moda-interact-commerce/tests/definition-execution.test.ts
moda-interact-commerce/tests/external-http-live-test.test.ts
moda-interact-commerce/tests/shopify-admin-live-test.test.ts
moda-interact-commerce/tests/external-publication.test.ts
```

Add a dedicated focused test file if that makes the optionality matrix clearer, for example:

```text
moda-interact-commerce/tests/result-template-optionality.test.ts
```

## Out of Scope

- C085 Result Template editor layout, CodeMirror configuration, autocomplete, insertion UX or available-result-data tree.
- Request-tab UI changes.
- Response-tab UI changes.
- Test-tab layout/presentation changes.
- Provider networking or provider response semantics.
- External/Shopify credential resolution.
- Tool persistence, ToolRevision persistence, audit or operation receipts.
- Publication-proof semantics.
- Changing the Response projection meaning of `Omit if missing`.
- Weakening result validation so a missing **required** field becomes acceptable.
- Globally disabling strict/undefined rendering merely to hide unsafe template access.
- Replacing missing optional values with invented strings such as `N/A`, `undefined`, `null` or an empty string.
- A general redesign of the C084 grammar. This task adds/uses only the presence semantics required to make optional access safe; any broader accepted C084 expression grammar remains unchanged.
- Any database, Shared, Background, Gateway, Admin or Shopify-app change.

## Requirements

### R1 — canonical totality invariant

For this task, define:

```text
CONTRACT-VALID RESULT
  = a CommerceToolResult success value whose `data` is accepted by the same
    canonical output/result schema used to validate the Tool's Response contract.
```

The required invariant is:

```text
For every CONTRACT-VALID RESULT R,
let T = generateDefaultResultTemplate(S),
where S is the canonical output schema that accepted R.

Then:
  validateResponseTemplateAuthoring(T, S) MUST be valid
and
  renderDefinitionResult(definitionWith(T), R) MUST NOT return/fail with
  RESULT_RENDERING_FAILED solely because a property that S permits to be
  omitted is absent from R.
```

This invariant applies recursively to:

```text
optional scalar properties
optional object properties
optional descendants of required objects
optional descendants of optional objects
optional array properties
optional fields inside array-of-object items
nested combinations of the above
```

Do not claim this invariant from generator inspection alone. Prove it with contract-valid fixtures in tests.

### R2 — schema optionality has one exact meaning

Derive required/optional property semantics only from the canonical object schema.

For an object schema:

```text
property P is REQUIRED
  iff P is present in the object's canonical `required` set.

property P is OPTIONAL
  iff P exists in canonical `properties` but is absent from `required`.
```

Do not infer optionality from:

```text
field name
sample value
whether the latest provider result happened to include the field
UI labels alone
truthiness
Nunjucks runtime behaviour
```

If C084 canonicalizes the Commerce result schema into an internal node model, use that canonical node model rather than independently reparsing raw JSON Schema in the generator and validator.

### R3 — add/use one explicit presence predicate

Optional access must be guarded by **presence**, not truthiness.

The canonical `nunjucks.v1` language after this task MUST support this bounded presence predicate inside an `if` condition:

```nunjucks
{% if <safe-path> is defined %}
  ...
{% endif %}
```

Examples:

```nunjucks
{% if item.description is defined %}
  Description: {{ item.description }}
{% endif %}
```

```nunjucks
{% if result.values.customer is defined %}
  ...
{% endif %}
```

`is defined` is a canonical presence test. It is not a general function call, custom filter or application callback.

If the architect-accepted C084 grammar already supports `if`/`elif` and the Nunjucks `defined` test, reuse that implementation. If `if` exists but `is defined` is not yet accepted, add **only** the `defined` presence-test support required here. Do not enable arbitrary Nunjucks tests.

If the accepted C084 implementation still has no conditional control-flow capability at all, add the minimum bounded `if`/`else`/`endif` handling required for these generated presence guards; do not use this correction as permission to invent unrelated grammar.

The canonical validator MUST reject unsupported tests such as arbitrary `is <test>` forms unless they are separately part of the accepted C084 grammar.

### R4 — presence must not be implemented with truthiness

The generator MUST NOT use:

```nunjucks
{% if item.id %}
{% if item.available %}
{% if item.name %}
```

as a substitute for presence checks.

The following values are **present values** and must remain distinguishable from an omitted property:

```text
0
false
""
```

Therefore generated optional-property guards use:

```nunjucks
{% if <path> is defined %}
```

not:

```nunjucks
{% if <path> %}
```

A present value of `0`, `false` or `""` must enter the guarded branch and be rendered according to the normal scalar rendering semantics.

### R5 — required scalars remain direct

For a required scalar property:

```text
name: string
```

with `name` present in the containing object's canonical `required` set, generation remains direct:

```nunjucks
Name: {{ item.name }}
```

Do not add redundant presence guards around required scalar fields.

If a required scalar is missing at runtime, canonical result validation must reject the result before template rendering. C087 must not normalize or hide that invalid result.

### R6 — optional scalars are guarded exactly once at their owning property

For an optional scalar property:

```text
description?: string
```

generate the semantic equivalent of:

```nunjucks
{% if item.description is defined %}
  Description: {{ item.description }}
{% endif %}
```

Rules:

```text
- the label/value line is inside the guard;
- absence emits no label and no invented fallback value;
- a present empty string still emits the label/value line;
- a present numeric zero still emits `0`;
- a present boolean false still emits `false` according to the canonical scalar renderer;
- the guard is generated from schema optionality, not from observed provider data.
```

### R7 — optional objects guard the whole object presentation recursively

For:

```text
customer?: {
  name: string
  email?: string
}
```

generate the semantic equivalent of:

```nunjucks
{% if result.values.customer is defined %}
  Customer:
  Name: {{ result.values.customer.name }}
  {% if result.values.customer.email is defined %}
    Email: {{ result.values.customer.email }}
  {% endif %}
{% endif %}
```

Required rules:

```text
- guard the optional object before dereferencing any child;
- required descendants may be dereferenced directly inside the object's guarded branch;
- optional descendants receive their own presence guards;
- nested optional objects apply the same rule recursively;
- do not emit the object's heading when the optional object is absent.
```

Do not generate a child-path presence test that first dereferences an unguarded optional parent.

INVALID generated shape:

```nunjucks
{% if result.values.customer.email is defined %}
```

when `customer` itself is optional and has not already been established as present.

### R8 — required arrays preserve the current deterministic loop shape

For a required array property, preserve C084's existing deterministic array generation except that optional descendants inside an object item are guarded according to this task.

For example, if `items` is required and its item properties are optional:

```nunjucks
Items:
{% for item in result.values.items %}
  {% if item.department is defined %}
    Department: {{ item.department }}
  {% endif %}
  {% if item.description is defined %}
    Description: {{ item.description }}
  {% endif %}
  {% if item.id is defined %}
    Id: {{ item.id }}
  {% endif %}
  {% if item.image is defined %}
    Image: {{ item.image }}
  {% endif %}
  {% if item.name is defined %}
    Name: {{ item.name }}
  {% endif %}
  {% if item.price is defined %}
    Price: {{ item.price }}
  {% endif %}
{% else %}
  No items available.
{% endfor %}
```

The property order remains the deterministic lexical order defined by C084.

### R9 — optional arrays have deterministic absent and empty semantics

For an optional array property, do not execute a `for` directly against an absent value.

Generate this semantic structure:

```nunjucks
<Label>:
{% if <array-path> is defined %}
  {% for itemN in <array-path> %}
    <generated item body>
  {% else %}
    No <lowercase label> available.
  {% endfor %}
{% else %}
  No <lowercase label> available.
{% endif %}
```

This defines:

```text
optional array absent   -> same generated empty/unavailable collection message
optional array present [] -> same generated empty/unavailable collection message
optional array present with items -> render items
```

Do not normalize an omitted array to `[]` in provider data merely to make the template work.

For a required array, do not add the outer `is defined` guard.

### R10 — arrays of objects apply optionality per item property

For an array-of-object item schema, determine each child property's optionality from the item object's canonical `required` set.

Example canonical item schema:

```text
required: [name]
properties:
  department: string
  description: string
  id: integer
  image: string
  name: string
  price: string
```

Generated semantics:

```nunjucks
{% for item in result.values.items %}
  {% if item.department is defined %}
    Department: {{ item.department }}
  {% endif %}
  {% if item.description is defined %}
    Description: {{ item.description }}
  {% endif %}
  {% if item.id is defined %}
    Id: {{ item.id }}
  {% endif %}
  {% if item.image is defined %}
    Image: {{ item.image }}
  {% endif %}
  Name: {{ item.name }}
  {% if item.price is defined %}
    Price: {{ item.price }}
  {% endif %}
{% endfor %}
```

Do not assume all projected fields share one optionality setting.

### R11 — generator output must still pass the canonical validator

After generation:

```ts
const template = generateDefaultResultTemplate(outputSchema);
const validation = validateResponseTemplateAuthoring(template, outputSchema);
```

must return canonical success.

Do not special-case generated templates in validation.

Generated templates and manually authored templates use the same validator and the same renderer.

If generator output fails the canonical validator, treat that as a generator defect and fail the focused test; do not whitelist generated source.

### R12 — canonical validator must reject unsafe optional dereferences

The canonical validator already receives the canonical output schema. Extend its semantic analysis so a template cannot be considered valid when it directly dereferences a schema-optional result path that is not proven present in the current control-flow scope.

Add stable issue code:

```text
unguarded_optional_result_path
```

with canonical issue path:

```text
/responseTemplate/source
```

Example invalid source when `description` is optional:

```nunjucks
Description: {{ item.description }}
```

Expected validation issue semantics:

```text
code: unguarded_optional_result_path
message: Optional result path "item.description" must be guarded by a supported presence check before use.
```

Keep the message bounded according to the existing C084 validation issue limits.

### R13 — exact presence-scope rules for validation

Presence analysis must be deterministic.

A positive standalone condition:

```nunjucks
{% if item.description is defined %}
```

establishes `item.description` as present **only inside that condition's positive branch**.

It does not establish presence:

```text
before the if
inside the else branch
after endif
inside a sibling branch
```

For an optional object:

```nunjucks
{% if result.values.customer is defined %}
```

establishes the object path `result.values.customer` as present inside the positive branch. Required descendants of that object may then be used directly. Optional descendants still require their own presence guards.

Do not infer presence from ordinary truthiness, comparison or arithmetic expressions.

For C087, presence dominance is recognized only from the canonical `is defined` predicate. If the broader C084 grammar supports compound boolean expressions, do not attempt speculative data-flow inference through `or`, arbitrary negation or unrelated expressions as part of this correction.

A child presence test is valid only when all optional ancestor paths required to evaluate it have already been established as present in the current validation scope.

### R14 — `for` collection paths must also be optional-safe

A supported `for` may consume an array path directly only when:

```text
- the collection path is required through every traversed property; OR
- every optional ancestor/collection property is established present by enclosing canonical presence guards.
```

Invalid when `items` is optional:

```nunjucks
{% for item in result.values.items %}
```

Valid:

```nunjucks
{% if result.values.items is defined %}
  {% for item in result.values.items %}
    ...
  {% endfor %}
{% endif %}
```

The generator must follow the same rule.

### R15 — do not fix this by making undefined globally permissive

Do not solve C087 by changing the Nunjucks environment so every undefined access silently renders as empty text.

Specifically, do not:

```text
- disable an existing strict/throw-on-undefined policy solely for this defect;
- catch undefined-property errors and convert them globally to empty strings;
- mutate the CommerceToolResult to insert arbitrary empty values for omitted optional fields;
- suppress canonical validator issues for optional paths.
```

The intended architecture is:

```text
Response contract optionality
        -> generator emits explicit safe presence guards
        -> canonical validator proves optional access is guarded
        -> renderer may remain strict
```

This keeps programmer/author mistakes visible while making generator output total over the schema.

### R16 — preserve required-field failure ownership

C087 must preserve this boundary:

```text
required field missing
        -> canonical result validation fails
        -> template rendering does not make the invalid result valid
```

and:

```text
optional field missing
        -> canonical result validation passes
        -> a canonical generated template renders successfully
```

Add an explicit regression proving both halves.

### R17 — exact observed-contract regression

Add a focused fixture matching the observed Response contract semantically:

```text
result.values.items[]
  department?: string
  description?: string
  id?: integer
  image?: string
  name?: string
  price?: string
```

`items` itself is required for this fixture.

The exact generated source must be semantically equivalent to:

```nunjucks
Items:
{% for item in result.values.items %}
  {% if item.department is defined %}
    Department: {{ item.department }}
  {% endif %}
  {% if item.description is defined %}
    Description: {{ item.description }}
  {% endif %}
  {% if item.id is defined %}
    Id: {{ item.id }}
  {% endif %}
  {% if item.image is defined %}
    Image: {{ item.image }}
  {% endif %}
  {% if item.name is defined %}
    Name: {{ item.name }}
  {% endif %}
  {% if item.price is defined %}
    Price: {{ item.price }}
  {% endif %}
{% else %}
  No items available.
{% endfor %}
```

The exact whitespace may follow the existing deterministic C084 indentation implementation, but the structural guard order and lexical property order above are mandatory.

Render at minimum these accepted values:

```json
{
  "values": {
    "items": [
      {
        "name": "Widget",
        "price": "12.99"
      }
    ]
  }
}
```

and, if permitted by the compiled contract:

```json
{
  "values": {
    "items": [
      {}
    ]
  }
}
```

Both must avoid `RESULT_RENDERING_FAILED` when they are contract-valid.

### R18 — falsy-present regression is mandatory

Add a separate schema fixture with optional scalar fields whose types permit:

```text
integer -> 0
boolean -> false
string  -> ""
```

Example accepted value:

```json
{
  "values": {
    "count": 0,
    "available": false,
    "label": ""
  }
}
```

The generated template must treat all three properties as **present**.

The test must fail if the implementation substitutes truthiness checks for `is defined`.

### R19 — nested optionality matrix is mandatory

Create a canonical schema fixture semantically equivalent to:

```text
values:
  requiredObject:
    requiredChild: string
    optionalChild?: string

  optionalObject?:
    requiredChild: string
    optionalChild?: string
    optionalGrandchildObject?:
      requiredLeaf: string
      optionalLeaf?: string

  optionalItems?: array<object>
    item:
      requiredField: string
      optionalField?: string
```

Render generator-produced templates against at least these contract-valid combinations:

```text
1. every optional value present
2. optionalChild omitted under requiredObject
3. optionalObject omitted
4. optionalObject present, optionalChild omitted
5. optionalGrandchildObject omitted
6. optionalGrandchildObject present, optionalLeaf omitted
7. optionalItems omitted
8. optionalItems present and empty
9. optionalItems present with item.optionalField omitted
10. all schema-permitted optional values omitted simultaneously
```

Every contract-valid case must render successfully.

### R20 — live-Test regressions must prove the integrated boundary

Use provider adapters/fixtures; do not call real providers.

For External HTTP live Test:

```text
provider fixture returns a result accepted by Response validation
with one or more schema-optional projected fields omitted
        -> resultValidation Passed
        -> resultRendering Passed
        -> renderedText is returned
        -> no RESULT_RENDERING_FAILED
```

For Shopify Admin live Test, add the equivalent regression if the canonical Admin result contract can express an optional omitted field in the focused fixture.

Do not redesign either Test UI. This is backend/domain regression coverage only.

### R21 — publication and preflight use the corrected canonical validator automatically

Do not implement optional-path checks separately in:

```text
External publication
Shopify publication
External Test preflight
Shopify Test preflight
React
```

Those boundaries must consume `validateResponseTemplateAuthoring` (or the single canonical C084 validator that replaced it).

A manually authored template containing an unguarded optional dereference must fail at canonical template validation before publication/provider I/O wherever current architecture already performs template preflight.

### R22 — no C085 UI redesign

C085 may surface the canonical validation issue returned by this task through its existing diagnostic path, but C087 MUST NOT redesign:

```text
CodeMirror
Available result data tree
autocomplete
insertions
Regenerate from Response controls
layout
styling
navigation
```

Do not add a UI-only optionality engine.

If existing C085 diagnostics cannot display the new canonical issue at all, report that exact integration gap to `moda_architect` rather than expanding C087 into an editor redesign.

## Work Items

- [x] Reproduce the observed `resultValidation Passed -> resultRendering Failed` case with a focused test and prove whether schema-permitted omission is the cause.
- [x] Confirm/centralize required-vs-optional property metadata in the canonical result-contract representation.
- [x] Add or reuse bounded `is defined` presence-test support required by this task.
- [x] Extend the default-template generator to guard optional scalar properties.
- [x] Extend the generator to guard optional objects before any child dereference.
- [x] Extend the generator recursively for optional descendants of required/optional objects.
- [x] Extend the generator with the exact optional-array absent/empty semantics in R9.
- [x] Preserve direct generation for required scalars and required collections.
- [x] Preserve deterministic lexical property ordering, aliasing and indentation from C084.
- [x] Extend the canonical Result Template validator with `unguarded_optional_result_path`.
- [x] Implement the exact presence-scope/dominance rules from R13/R14.
- [x] Keep the Nunjucks renderer strict; do not globally hide undefined access.
- [x] Add the exact observed `values.items[]` regression from R17.
- [x] Add falsy-present regressions for `0`, `false` and `""`.
- [x] Add the nested optionality matrix from R19.
- [x] Add External live-Test regression proving resultRendering passes with omitted optional projected fields.
- [x] Add Shopify Admin equivalent where the focused Admin contract supports optional omission.
- [x] Prove missing required fields still fail result validation and are not normalized away.
- [x] Prove a manually authored unguarded optional dereference fails canonical template validation.
- [x] Run the focused C084 generator/validator/renderer/publication/Test packet plus required repository checks.

## Interfaces / Contracts

Consumes and corrects Commerce-owned boundaries introduced/owned by C084:

```text
generateDefaultResultTemplate(outputSchema)
validateResponseTemplateAuthoring(template, outputSchema)
ResponseTemplate / nunjucks.v1 contract
renderDefinitionResult(definition, result, ...)
canonical Commerce result/output schema
```

Consumes existing provider Test boundaries without changing their transport contracts:

```text
C080 External HTTP non-durable Test
C082 Shopify Admin non-durable Test
```

Adds canonical validation issue code:

```text
unguarded_optional_result_path
```

Adds/standardizes the bounded presence predicate:

```nunjucks
<safe-path> is defined
```

No database or cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-084

C085 is deliberately **not** a dependency. The defect belongs to generator/validator/renderer semantics and must be correct independently of the editor.

## Enables

None directly.

The architect should add C087 to any not-yet-executed ARCH-021 terminal system-test dependency set that validates Result Template live rendering. Do not make another implementation task depend on a system-test task.

## Acceptance Criteria

- [x] The observed optional-field rendering failure is reproduced and its root cause is documented in the Completion Report.
- [x] If the observed failure is not caused by schema-permitted omission, no unrelated renderer change is made and the task is returned Blocked with evidence.
- [x] Required/optional property semantics are derived only from the canonical result contract.
- [x] `nunjucks.v1` supports the bounded `is defined` presence predicate required for optional guards.
- [x] Generated optional scalar accesses use presence guards, not truthiness guards.
- [x] Generated required scalar accesses remain direct.
- [x] Generated optional objects are guarded before child dereference.
- [x] Optional descendants are guarded recursively.
- [x] Required arrays preserve the current loop shape apart from guards required inside their item body.
- [x] Optional arrays render the same deterministic `No <label> available.` message when absent or present-empty.
- [x] Generator output remains deterministic and passes the canonical Result Template validator.
- [x] The canonical validator reports `unguarded_optional_result_path` for unsafe direct access to an optional result path.
- [x] Presence established by an `is defined` guard is scoped exactly to the positive branch and does not leak after `endif` or into `else`.
- [x] Optional collection paths cannot be used by `for` unless required or proven present.
- [x] `0`, `false` and `""` are treated as present values and are not mistaken for omission.
- [x] Missing required properties still fail canonical result validation.
- [x] No schema-permitted omitted optional scalar/object/collection in the mandatory matrix causes generated-template `RESULT_RENDERING_FAILED`.
- [x] The exact `values.items[]` regression with omitted projected fields renders successfully.
- [x] External live Test reports `resultRendering Passed` and returns `renderedText` for the omitted-optional-field fixture.
- [x] Shopify Admin equivalent passes where the focused contract supports the same optionality case.
- [x] No provider-specific optionality validator or renderer is introduced.
- [x] No C085 UI redesign is included.
- [x] No durable Tool/Test/publication-proof write is introduced.

## Validation

Run the actual scripts declared by `moda-interact-commerce/package.json`; do not invent missing repository scripts.

Required focused validation includes:

- [x] focused unit test reproducing the originally observed rendering failure before the fix and passing after the fix;
- [x] Result Template generator deterministic snapshot/assertions for required vs optional fields;
- [x] canonical validator tests for `unguarded_optional_result_path`;
- [x] positive/negative presence-scope tests (`if ... is defined`, `else`, after `endif`, optional parent + optional child);
- [x] falsy-present tests for `0`, `false`, `""`;
- [x] nested optionality matrix from R19;
- [x] result-validation regression proving a missing required property is rejected;
- [x] External live-Test regression with omitted optional projected fields;
- [x] Shopify Admin live-Test equivalent where applicable;
- [x] existing C084 Result Template authoring/generator/renderer tests;
- [x] existing publication template-validation tests affected by the canonical validator;
- [x] targeted ESLint for every changed source/test file;
- [x] changed-file TypeScript diagnostics, or repository typecheck with known-baseline reconciliation;
- [x] `git diff --check`.

When reporting live-Test validation, record the stage outcomes explicitly. The required fixed External regression must show semantically:

```text
resultValidation  Passed
resultRendering   Passed
```

If a required test cannot execute because of an existing documented baseline condition, reference the baseline ID and prove C087 changed files introduce no new failure. Do not silently mark the validation item complete.

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete:

1. finish the Completion Report;
2. set the task to `review`;
3. clear/record execution metadata according to the normal task workflow;
4. return control to `moda_architect`;
5. STOP.

Do not begin C085/C081/C083, a system-test task, UI cleanup, or another adjacent capability from this task.

## Implementation Notes

The key architectural distinction is:

```text
OPTIONALITY
  = whether a property may be absent according to the Response/result contract.

TRUTHINESS
  = the runtime value of a property that is present.
```

Never use truthiness to implement optionality.

Prefer explicit generated presence guards and semantic validation over permissive undefined rendering. The generator should produce templates that are safe by construction, and the validator should prevent a manually authored template from reintroducing the same failure mode.

Do not add a second optionality interpretation in React, provider Test code or publication code.

If source inspection shows C084 already deliberately defines absent optional scalar interpolation as safe without a guard **and** the renderer proves that contract for all supported scalar types under strict tests, return that evidence to `moda_architect` before adding redundant guards. Do not silently diverge from an already accepted canonical C084 semantic contract.

## Completion Report

### Status

Attempt 1 implementation complete; submitted for Architect Review.

### Files Changed

`moda-interact-commerce/src/commerce/execution/renderer.ts`
`moda-interact-commerce/src/commerce/tool-authoring/nunjucks-template.ts`
`moda-interact-commerce/src/commerce/tool-authoring/result-template-generator.ts`
`moda-interact-commerce/tests/definition-execution.test.ts`
`moda-interact-commerce/tests/external-http-live-test.test.ts`
`moda-interact-commerce/tests/result-template-authoring.test.ts`
`moda-interact-commerce/tests/result-template-optionality.test.ts`
`moda-interact-commerce/tests/result-template-renderer.test.ts`

### Work Completed

- Reproduced the C084 boundary mismatch: canonical normalization accepts omitted optional properties, while a direct strict Nunjucks lookup fails on the absent value. The External live-Test regression now proves `resultValidation: Passed` and `resultRendering: Passed` for that same permitted omission.
- Generated templates use canonical `required` membership at root and nested object boundaries. Optional scalar/object paths are guarded with `is defined`; absent optional arrays use the deterministic unavailable-for-collection message, including when present-empty; required scalar paths remain direct.
- The canonical validator recognizes only the bounded `is defined` AST test, tracks positive-branch presence without leaking scope, validates optional loop sources, and reports `unguarded_optional_result_path` for unsafe accesses.
- Registered the `defined` test in the existing strict renderer without changing `throwOnUndefined`. A local intersection type describes the runtime `addTest` API omitted from the installed Nunjucks declaration.
- Added the exact six-optional-field item fixture, empty-item rendering, nested optionality matrix, falsy-present values, top-level optionality, required-field rejection, unsafe-authored-template cases, External live-Test coverage and a Shopify Admin canonical execution regression.
- The C087 implementation commit changes no C085 UI/state files, provider-specific validators, persisted template shape, publication-proof writes or durable Test writes. C085 files visible in the task branch are unchanged files brought in by the required `origin/main` merge.

### Validation Results

- Final focused C087 packet after merging current `origin/main`: 11 files passed, 132 tests passed. It covers generator, canonical validator, renderer, Admin definition execution, External live Test, publication/preflight and commerce lifecycle boundaries.
- External omitted-optional-field Test asserts `resultValidation: passed`, `resultRendering: passed`, and returned rendered text. Missing required data remains rejected before rendering. Shopify Admin coverage uses a compiler-supported nullable selected field, canonical omission normalization and the production definition executor; no Admin Test UI is introduced by this task.
- Targeted ESLint on all eight changed files passed. VS Code changed-file diagnostics reported no errors. Project-wide `tsc --noEmit` remains nonzero on unrelated C085 Result Template tab test diagnostics (`tests/result-template-tab.test.tsx`); filtered diagnostics contain no C087-changed file. C084 Attempt 2 also records a broad pre-existing repository typecheck baseline.
- `git diff --check` passed before commit and after mainline synchronization.
- A 12-file supplemental run passed 152/154 tests. Its two failures are existing QuickJS request-preview cases in `tests/external-tool-authoring-validation.test.ts`: the packaged runtime reports `MODULE_NOT_FOUND`, producing `RUNTIME_UNAVAILABLE`. C084 Attempt 1 documents the same QuickJS preview baseline; the C087-focused 11-file packet passes when those unrelated cases are excluded.

### Deviations

- The repository has no Shopify Admin live-Test action/test integration yet; that UI integration is explicitly owned by C083 and is out of scope here. The Admin production-execution regression covers the same canonical optional-result and strict-rendering path.
- Whole-project typecheck and the two QuickJS-dependent external-authoring tests remain limited by the documented repository/runtime baseline; no C087-changed file is implicated.

### Assumptions

The C082/C083 Admin live-Test surface will consume the same canonical renderer; C087 does not add a second provider-specific presence implementation.

### Unresolved Issues

No C087-owned issue remains. The existing QuickJS `MODULE_NOT_FOUND` preview condition and unrelated C085/repository type diagnostics are recorded above for Architect review.

### Architectural Concerns

None. Strict undefined rendering, the persisted `nunjucks.v1` shape, canonical schema ownership and C085 UI ownership are preserved.

### Git / VCS

Task branch: `task/ARCH-021-COMMERCE-087`

Physical worktree isolation:
- canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-087`
- parent branch: `task/ARCH-021-COMMERCE-087`
- implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-087`
- implementation branch: `task/ARCH-021-COMMERCE-087`
- shared workspace checkout switched/mutated for task work: no
- shared implementation checkout switched/mutated for task work: no
- another task worktree reused: no

Start-of-attempt synchronization:
- parent remote task branch fast-forwarded: yes (launcher-prepared; verified current before report update)
- parent `origin/main` incorporated: yes
- implementation remote task branch fast-forwarded: not-needed (no remote task ref existed before publication)
- implementation `origin/main` incorporated: yes

Implementation repository:
- repository: `moda-interact-commerce`
- implementation commit: `8905d9b` (C087 implementation `dfefb3f`; mainline merge `8905d9b`)
- remote branch: `origin/task/ARCH-021-COMMERCE-087`
- pushed: yes

Parent workspace:
- task file: `docs/decisions/commerce/ARCH-021/COMMERCE-087-make-generated-nunjucks-optional-safe.md`
- commit: `072447753bd85d7fd7fa91c7c93d5e69c036444c` (completion report)
- remote branch: `origin/task/ARCH-021-COMMERCE-087`
- pushed: yes
- submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

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
