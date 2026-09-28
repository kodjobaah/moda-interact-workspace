---
id: ARCH-021-COMMERCE-084
architecture_id: ARCH-021
title: Replace Result Template runtime with constrained Nunjucks v1
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 75
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-063
  - ARCH-021-COMMERCE-078
  - ARCH-021-COMMERCE-080
  - ARCH-021-COMMERCE-082
enables:
  - ARCH-021-COMMERCE-085
created: 2026-09-28
updated: 2026-09-28
---

# Replace Result Template runtime with constrained Nunjucks v1

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Replace the current bespoke `text` / `items` Result Template grammar with one Commerce-owned, bounded `nunjucks.v1` template-source contract, add deterministic schema-to-template generation, and make publication, non-durable Test and production execution validate/render the same template language through one canonical boundary.

## Context

The current implementation stores one of two response-template objects:

```text
kind: text
kind: items
```

That split forces the author to choose a presentation mode before the Tool has interpreted the Response shape. It also treats collections as a special UI/runtime case even though the canonical Response contract already describes objects, scalars and bounded arrays recursively.

The agreed replacement is:

```text
canonical Response/output schema
        |
        +--> deterministic default-template generator
        |
        v
bounded Nunjucks source
        |
        +--> canonical schema-aware validator
        |
        +--> Test renderer
        |
        +--> production renderer
```

The language is **not unrestricted Nunjucks**. This task defines and enforces the exact `nunjucks.v1` subset Moda supports. COMMERCE-085 owns the CodeMirror authoring UI over this runtime contract.

ARCH-021 is already classified PRE-PRODUCTION / BREAKING ROLLOUT. No production compatibility requirement exists for the current `text` / `items` Result Template grammar.

## Scope

Primary implementation areas:

```text
moda-interact-commerce/package.json
moda-interact-commerce/package-lock.json

moda-interact-commerce/src/commerce/tool-definition/contracts.ts
moda-interact-commerce/src/commerce/tool-definition/publication.ts
moda-interact-commerce/src/commerce/tool-definition/response-template-syntax.ts

moda-interact-commerce/src/commerce/tool-authoring/result-template-contract.ts
moda-interact-commerce/src/commerce/tool-authoring/result-template-generator.ts     # new
moda-interact-commerce/src/commerce/tool-authoring/nunjucks-template.ts            # new bounded parser/validator helpers, or equivalent

moda-interact-commerce/src/commerce/execution/renderer.ts
```

Tests include, as applicable:

```text
moda-interact-commerce/tests/arch021-commerce-tool-contract.test.ts
moda-interact-commerce/tests/result-template-authoring.test.ts
moda-interact-commerce/tests/definition-execution.test.ts
moda-interact-commerce/tests/external-http-live-test.test.ts
moda-interact-commerce/tests/shopify-admin-live-test.test.ts
moda-interact-commerce/tests/external-publication.test.ts
moda-interact-commerce/tests/shopify-admin-authoring-validation.test.ts
```

Update Commerce-owned fixtures/tests that still construct the obsolete `text` / `items` grammar. Do not modify another repository merely to keep an obsolete fixture shape alive.

## Out of Scope

- The CodeMirror Result Template editor and authoring UX; COMMERCE-085.
- Request, Response or Test-tab presentation changes.
- Persisted-DRAFT parity/navigation; COMMERCE-079 consumes COMMERCE-085.
- External/Shopify Test UI integration; COMMERCE-081/083 consume COMMERCE-085.
- Arbitrary JavaScript in templates.
- Full Nunjucks language support.
- HTML/WYSIWYG rendering.
- Includes, imports, macros, inheritance, filesystem/network loaders or template files.
- Database schema/migrations. `responseTemplate` is already stored as JSONB inside the Commerce Tool definition.
- A legacy `text` / `items` compatibility adapter. This is a pre-production breaking replacement.
- Changes to Background, Gateway, Shopify app or Admin repositories.
- Changes to `@modainteract/moda-interact-shared` unless source inspection proves that the production Tool-definition/response-template contract crosses a service boundary. If such a consumer is discovered, STOP and return the ownership issue to `moda_architect`; do not edit Shared from this task.

## Requirements

### R1 — one canonical persisted Result Template shape

Replace the current `ResponseTemplateSchema` union with exactly one semantic shape:

```ts
type ResponseTemplate = {
  kind: "nunjucks";
  runtimeVersion: "nunjucks.v1";
  source: string;
  unavailable: string;
};
```

Schema requirements:

```text
kind            = literal "nunjucks"
runtimeVersion  = literal "nunjucks.v1"
source          = non-empty after trim
source          = <= 8192 UTF-8 bytes
unavailable     = <= 4096 characters
```

`unavailable` is plain output text. It is not parsed as Nunjucks.

`CommerceToolDefinitionSchema` must require this new shape. `CommerceToolDraftDefinitionSchema` remains permissive enough for incomplete browser-local authoring exactly as today; do not weaken the final Definition schema.

Do not retain `kind: text` or `kind: items` in the final Definition schema.

### R2 — install Nunjucks as a direct Commerce runtime dependency

Add `nunjucks` as a direct `moda-interact-commerce` runtime dependency using the repository package manager. Let the generated lockfile record the exact resolved version. Add the maintained type package as a dev dependency only if TypeScript requires it.

Do not copy Nunjucks source into the repository and do not add a second template engine.

Nunjucks must be imported only by Commerce server/domain runtime code. COMMERCE-085 client components must not bundle the Nunjucks runtime merely to edit source text.

### R3 — supported `nunjucks.v1` grammar is intentionally bounded

The canonical validator must accept only these semantic constructs:

```text
1. Literal text.
2. Scalar interpolation:
     {{ result.path.to.scalar }}
3. Loop-local scalar interpolation:
     {{ item.path.to.scalar }}
   where `item` is the alias introduced by an enclosing supported `for`.
4. Scalar-array item interpolation:
     {{ item }}
   when the enclosing loop iterates an array of scalar values.
5. Bounded loops:
     {% for item in result.path.to.array %}
       ...
     {% else %}
       ...
     {% endfor %}
6. Nested loops over an array reachable from the current root/loop alias.
```

A loop alias may be any safe identifier accepted by the existing Commerce safe-name rules except reserved names. It must not be `result`, `constructor`, `prototype` or `__proto__`, and it must not shadow an already-active loop alias.

The following are **not supported in `nunjucks.v1`** and must produce deterministic validation issues:

```text
if / elif
set
macro / call
include / import / from / extends / block
filters (`|`)
function calls
arithmetic
comparisons
boolean expressions
array/object literals
bracket/index access
computed property access
comments/raw blocks if they require bypassing normal validation
Nunjucks globals such as range/cycler/joiner
`loop.*`
```

Do not silently accept an unsupported Nunjucks construct because the upstream Nunjucks engine happens to understand it.

### R4 — result paths are contract-validated, not just syntactically valid

Validation receives:

```ts
validateResponseTemplateAuthoring(
  template: unknown,
  outputSchema: unknown,
): ResultTemplateValidation
```

Preserve this canonical authoring boundary rather than creating a second UI-only validator.

For each supported expression:

```text
{{ result.x.y }}
```

`x.y` must resolve to a scalar in the supplied canonical output schema.

For:

```text
{% for item in result.values.items %}
```

`values.items` must resolve to an array in the supplied canonical output schema.

Inside that loop:

```text
{{ item.name }}
```

must resolve to a scalar under the array item schema.

If the array item itself is scalar, `{{ item }}` is valid and `{{ item.foo }}` is invalid.

If the array item is an object, `{{ item }}` is invalid and scalar descendants are valid.

Arrays may only be consumed by a supported `for`; they may not be interpolated directly.

Objects may not be interpolated directly.

Unsafe path segments remain forbidden:

```text
__proto__
prototype
constructor
```

### R5 — deterministic complexity bounds

Reject a template as `template_too_complex` before rendering if any limit is exceeded:

```text
source UTF-8 bytes     > 8192
parsed template nodes  > 256
nested for depth       > 4
total for blocks       > 16
```

Existing Commerce result schemas already bound arrays to `maxItems <= 20`; preserve that invariant.

Validation issues remain bounded to at most 32 issues and 512 characters per path/code/message as in the current Result Template contract.

Use these stable issue codes where applicable:

```text
invalid_template_shape
invalid_template_syntax
unsupported_template_construct
unsafe_template_path
invalid_result_path
invalid_collection_path
invalid_loop_alias
template_too_complex
template_generation_too_large
```

Template-source issues use the canonical path:

```text
/responseTemplate/source
```

Unavailable-fallback shape issues use:

```text
/responseTemplate/unavailable
```

### R6 — server rendering is isolated from application capabilities

Create one Nunjucks Environment for this bounded renderer with:

```text
no filesystem loader
no network loader
no application-provided globals
no application-provided callable functions
no application-provided custom filters
synchronous rendering only
```

Static validation is mandatory even though the Nunjucks environment is restricted.

Before rendering, convert `result.data` to a JSON-only, getter-free, recursively null-prototype data tree. The template context exposes exactly:

```ts
{
  result: sanitizedResultData
}
```

No request object, process/environment object, service object, credentials, connection state or application functions are exposed.

Rendering is plain text. Do not treat the rendered result as trusted HTML and do not add `dangerouslySetInnerHTML` anywhere.

### R7 — one renderer for Test and production

`renderDefinitionResult` remains the only production/Test template-rendering boundary.

For a successful `CommerceToolResult`:

```text
validate/assume validated nunjucks.v1 definition
        -> render source against { result: result.data }
        -> bounded renderedText
```

For `result.status === ERROR`, return the existing Tool result with:

```text
renderedText = responseTemplate.unavailable
```

If Nunjucks rendering throws, violates the template grammar unexpectedly or produces output longer than 4096 characters, return the same safe failure semantics used by the current renderer with:

```text
renderedText = responseTemplate.unavailable
```

Do not allow a renderer exception to escape into provider execution or MCP execution.

COMMERCE-080 External Test and COMMERCE-082 Shopify Admin Test must continue to receive agent-facing text exclusively through `renderDefinitionResult`; do not add provider-specific rendering.

### R8 — deterministic default-template generator

Add one pure, provider-neutral generator:

```ts
generateDefaultResultTemplate(
  outputSchema: CommerceResultSchema,
  unavailable?: string,
): ResponseTemplate
```

Default `unavailable` when omitted:

```text
Information is unavailable.
```

The generator must not inspect Shopify or External provider definitions. It consumes only the canonical Commerce result schema supplied to Result Template authoring.

Generation order is deterministic:

```text
object property names: ascending lexical order
array aliases:          item, item2, item3, item4 by loop depth
indentation:            two spaces per nested presentation level
newline:                \n
trailing newline:       none
```

Human labels use the existing Result Template humanisation rule:

```text
camelCase -> Camel Case
snake_case -> Snake Case
kebab-case -> Kebab Case
```

Generator rules:

```text
SCALAR NODE
  <Label>: {{ <expression> }}

OBJECT NODE
  recurse through children in lexical order.
  Do not emit a synthetic heading for the canonical top-level `values` wrapper.
  For any other named nested object, emit `<Label>:` then its children indented by two spaces.

ARRAY OF OBJECTS
  <Label>:
  {% for itemN in <array-expression> %}
    <generated item object body>
  {% else %}
    No <lowercase label> available.
  {% endfor %}

ARRAY OF SCALARS
  <Label>:
  {% for itemN in <array-expression> %}
    - {{ itemN }}
  {% else %}
    No <lowercase label> available.
  {% endfor %}
```

For the manual-review Response contract:

```text
result.values.items[]
  department: string
  description: string
  id: integer
  image: string
  name: string
  price: string
```

the generated source must be exactly equivalent to:

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

Property order above is lexical and therefore deterministic.

If deterministic generation would exceed the canonical 8192-byte source bound, fail explicitly with `template_generation_too_large`. Do not truncate generated source.

### R9 — publication validates the same grammar

`validateDefinitionForPublication`, External publication and Shopify Admin definition validation must use the canonical `validateResponseTemplateAuthoring` result against the provider/compiler canonical output schema.

A template that uses an unsupported construct or a path absent from the current result contract must fail before publication and before live provider I/O where current Test preflight already performs template validation.

Do not maintain one template rule for authoring and another for publication/runtime.

### R10 — no legacy runtime branch

Remove the old `text` / `items` runtime branching from:

```text
ResponseTemplateSchema
result-template syntax helpers
validateResponseTemplateAuthoring
renderDefinitionResult
Commerce-owned fixtures/tests
```

Do not introduce:

```text
if (template.kind === "text") ...
else if (template.kind === "items") ...
```

as compatibility code.

Because this capability is pre-production, existing local development Tool revisions using the old grammar may become invalid and must be recreated/re-authored. Record that behaviour in the Completion Report. Do not add a database migration solely for development fixtures.

### R11 — source-of-truth/ownership audit

Before implementation, perform this bounded source audit:

```text
Search non-Commerce deployable source for imports/validation of the Commerce Tool
responseTemplate or CommerceToolDefinition runtime schema.
```

Expected result from the architecture snapshot is that Tool-definition execution remains Commerce-owned and no other deployable service consumes this Result Template runtime grammar.

If a real non-Commerce runtime consumer is found, STOP before changing the grammar and report the exact consumer to `moda_architect`. Do not create a duplicate contract and do not modify another repository from this task.

## Work Items

- [ ] Perform the bounded Result Template ownership/source audit from R11.
- [ ] Add direct Nunjucks runtime dependency and lockfile update.
- [ ] Replace `ResponseTemplateSchema` with the exact `nunjucks.v1` shape.
- [ ] Implement the bounded supported-language parser/static validator and stable issue codes.
- [ ] Validate interpolation and loop paths against the canonical `CommerceResultSchema`.
- [ ] Enforce source/node/loop/depth bounds.
- [ ] Add JSON-only/null-prototype render-context sanitization.
- [ ] Replace `renderDefinitionResult` text/items branches with the one Nunjucks renderer.
- [ ] Add the deterministic provider-neutral default-template generator.
- [ ] Make publication and current live-Test preflight consume the same canonical validator/renderer.
- [ ] Remove obsolete text/items syntax/runtime branches.
- [ ] Convert Commerce-owned fixtures/tests to `nunjucks.v1`.
- [ ] Add bounded security, generation, validation and rendering regressions.

## Interfaces / Contracts

Produces Commerce-local contracts:

```ts
ResponseTemplate = {
  kind: "nunjucks";
  runtimeVersion: "nunjucks.v1";
  source: string;
  unavailable: string;
}

generateDefaultResultTemplate(outputSchema, unavailable?)
validateResponseTemplateAuthoring(template, outputSchema)
renderDefinitionResult(definition, result, limits)
```

Consumes:

```text
CommerceResultSchema / CommerceResultSchemaSchema
COMMERCE-063 canonical Result Template/output-schema compatibility boundary
COMMERCE-080 External complete-candidate live Test
COMMERCE-082 Shopify Admin complete-candidate live Test
```

No new database or cross-repository contract is introduced unless R11 proves the current architecture snapshot is incomplete; that condition blocks the task for architect review.

## Dependencies

- ARCH-021-COMMERCE-063
- ARCH-021-COMMERCE-078
- ARCH-021-COMMERCE-080
- ARCH-021-COMMERCE-082

## Enables

- ARCH-021-COMMERCE-085

## Acceptance Criteria

- [ ] Final Commerce Tool definitions accept only `kind: "nunjucks"`, `runtimeVersion: "nunjucks.v1"` Result Templates.
- [ ] Legacy final `text` and `items` templates are rejected; no compatibility runtime branch remains.
- [ ] Supported scalar interpolation and bounded `for`/`else` loops render correctly for scalar, object, object-list, scalar-list and nested-list result schemas.
- [ ] Unsupported Nunjucks constructs are rejected deterministically before render/provider I/O.
- [ ] Every interpolated scalar path and every loop collection path is proven against the current canonical result contract.
- [ ] No template can access prototype paths, functions, globals, loaders, environment variables, credentials or application service objects.
- [ ] Renderer output remains bounded to 4096 characters and renderer failures fall back without escaping exceptions.
- [ ] The deterministic generator produces the exact expected source for the documented `values.items[]` example.
- [ ] Generator output is provider-neutral and stable for identical canonical schemas.
- [ ] External and Shopify live-Test backends continue to use the production renderer and remain zero-write.
- [ ] Publication rejects invalid/incompatible Nunjucks source through the canonical validation boundary.
- [ ] No database migration or non-Commerce implementation change is introduced.

## Validation

- [ ] `npx vitest run tests/arch021-commerce-tool-contract.test.ts tests/result-template-authoring.test.ts tests/definition-execution.test.ts`
- [ ] `npx vitest run tests/external-http-live-test.test.ts tests/shopify-admin-live-test.test.ts`
- [ ] focused generator fixtures for scalar/object/object-list/scalar-list/nested-list schemas
- [ ] focused rejection tests for each unsupported construct listed in R3
- [ ] focused rejection tests for unsafe/unknown paths and non-array loop sources
- [ ] focused complexity-bound tests for source bytes, AST nodes, loop count and nesting depth
- [ ] focused renderer tests for Error fallback, empty list `else`, optional missing values and 4096-character output bound
- [ ] focused proof that invalid template preflight causes zero provider I/O in External and Shopify Test
- [ ] bounded source audit proving no non-Commerce runtime consumer was silently changed
- [ ] targeted ESLint for changed files
- [ ] changed-file TypeScript diagnostics, or repository typecheck with baseline reconciliation
- [ ] `git diff --check`

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not begin COMMERCE-085 or any dependent task.

## Implementation Notes

Do not treat Nunjucks as a sandbox. Moda's security boundary is the combination of a severely restricted accepted grammar, schema-aware path validation, JSON-only/null-prototype context, no loaders/functions/globals and bounded source/result data. If the chosen Nunjucks API cannot support those invariants cleanly, stop and report the concrete incompatibility rather than weakening the language restrictions.

The default generator is an authoring convenience, not a second runtime grammar. It emits ordinary `nunjucks.v1` source that must pass the same canonical validator as user-authored source.

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
