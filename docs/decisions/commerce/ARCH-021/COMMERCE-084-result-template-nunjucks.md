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
status: review
priority: 75
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-021-COMMERCE-063
  - ARCH-021-COMMERCE-078
  - ARCH-021-COMMERCE-080
  - ARCH-021-COMMERCE-082
enables:
  - ARCH-021-COMMERCE-085
created: 2026-09-28
updated: 2026-09-29
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
- Persisted-DRAFT lifecycle/CAS/navigation semantics remain owned by the already-complete COMMERCE-079; COMMERCE-085 must preserve them while replacing the Result Template editor.
- External live-Test presentation/gating remains owned by the already-complete COMMERCE-081 and must be preserved by COMMERCE-085; Shopify Admin Test UI integration remains COMMERCE-083 and is dependency-gated by COMMERCE-085.
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

The canonical validator MUST first parse the source using the installed Nunjucks parser/AST. Nunjucks parse success is necessary but is **not sufficient**. Moda must then traverse that AST through its own explicit allowlist and schema-aware semantic validator.

Do not use a hand-written delimiter/path scanner as the sole syntax parser. The canonical validator must never accept source that the installed Nunjucks parser rejects.

The canonical validator MUST accept only the following semantic constructs.

#### 1. Literal text

Any bounded literal output text is allowed.

#### 2. Path interpolation

```nunjucks
{{ result.path.to.scalar }}
```

and, inside a supported loop:

```nunjucks
{{ item.path.to.scalar }}
```

For scalar-array loops:

```nunjucks
{{ item }}
```

A root scalar result may be interpolated as:

```nunjucks
{{ result }}
```

only when the canonical root `CommerceResultSchema` is scalar.

Supported numeric arithmetic expressions from section 8 may also be interpolated.

All referenced paths MUST resolve against the current `ToolResultContract` / canonical `CommerceResultSchema` and active loop scope.

#### 3. Bounded `for` loops

```nunjucks
{% for item in result.path.to.array %}
  ...
{% else %}
  ...
{% endfor %}
```

A root array may be consumed as:

```nunjucks
{% for item in result %}
```

only when the canonical root result schema is an array.

Nested supported loops are allowed when the collection path resolves to an array reachable from `result` or an active loop alias.

Loop aliases follow the existing Commerce safe-name rules and MUST NOT:

```text
equal result
equal constructor
equal prototype
equal __proto__
shadow an already-active loop alias
```

The accepted alias must also be syntactically valid for the installed Nunjucks parser; do not admit a Commerce-safe identifier that Nunjucks parses as a keyword or non-identifier.

#### 4. Conditional control flow

Support:

```nunjucks
{% if expression %}
  ...
{% elif expression %}
  ...
{% else %}
  ...
{% endif %}
```

`elif` MAY occur zero or more times.

`else` is optional.

Nested supported `if` and `for` blocks are permitted within the existing template nesting limit.

#### 5. Primitive literals

Expressions MAY contain:

```text
string literals
numeric literals
true
false
null
```

Do not support array or object literals in `nunjucks.v1`.

#### 6. Comparisons

Support exactly:

```text
==
!=
<
<=
>
>=
```

Comparison operands may be:

```text
valid result/loop-alias paths
primitive literals
supported arithmetic expressions
```

Equality/inequality must reject incompatible operand types rather than relying on coercion. Integer and number operands are numeric-compatible.

Ordering comparisons `< <= > >=` MUST operate only on compatible scalar types. Numeric/integer pairs are compatible; string/string ordering is permitted; boolean and null ordering is not.

Invalid type combinations MUST produce a deterministic validation issue rather than relying on Nunjucks/JavaScript coercion.

#### 7. Boolean expressions

Support exactly:

```text
and
or
not
```

Parentheses MAY be used for grouping:

```nunjucks
{% if item.available and (item.price < 50 or item.onSale) %}
```

Operator precedence MUST follow:

```text
parentheses
arithmetic
comparisons
not
and
or
```

`and`, `or` and `not` operands must be statically boolean-valued. A boolean result path or comparison expression is boolean-valued.

An `if` / `elif` condition must be statically boolean-valued.

Do not allow function calls or expressions with side effects.

#### 8. Numeric arithmetic

Support exactly:

```text
+
-
*
/
%
```

and unary numeric negation:

```text
-value
```

Arithmetic operands MUST resolve to numeric values (`integer` / `number`) or numeric literals.

Do not use `+` for implicit string concatenation.

Example:

```nunjucks
{{ result.values.subtotal * 1.2 }}
```

Invalid arithmetic operand types MUST fail canonical template validation.

Division or modulo by zero MUST result in a deterministic render failure. It MUST NOT emit `Infinity`, `NaN` or engine-dependent output. At the `CommerceToolResult` boundary this failure continues to map to the existing safe `INVALID_INPUT` + `responseTemplate.unavailable` semantics; do not introduce a new cross-repository Tool-result error enum solely for template arithmetic.

#### 9. Path access

Supported path syntax remains property-only:

```text
identifier(.identifier)*
```

Examples:

```text
result.values.total
item.name
product.variant.price
```

Continue to prohibit:

```text
bracket access
numeric indexing
computed properties
prototype-related names
```

Every path must be statically resolvable against the `CommerceResultSchema` and active loop scope.

#### 10. Type-aware semantic validation

Parsing successfully with Nunjucks is NOT sufficient.

Moda's canonical validator MUST validate expression semantics against the Response/result contract.

Examples:

If:

```text
item.name     -> string
item.price    -> number
item.inStock  -> boolean
```

then these are valid:

```nunjucks
{{ item.price * 1.2 }}

{% if item.price <= 50 %}

{% if item.inStock and item.price < 50 %}

{% if item.name == "Widget" %}
```

This MUST fail validation:

```nunjucks
{{ item.name * 10 }}
```

because multiplication requires numeric operands.

This MUST also fail:

```nunjucks
{% if item.unknownField %}
```

because the path does not exist in the Response contract.

Use one stable validation issue code for a syntactically-supported expression whose operand/result types are invalid:

```text
invalid_template_expression
```

The following remain **unsupported in `nunjucks.v1`** and MUST produce deterministic validation issues:

```text
set
macro / call
include / import / from / extends / block
filters (|)
function calls
method calls
assignments
array literals
object literals
bracket/index access
computed property access
Nunjucks globals such as range/cycler/joiner
loop.*
arbitrary registered globals/functions
dynamic template loading
```

Comments MAY be supported only when they are parsed by the canonical Nunjucks parser and ignored by Moda's semantic validator:

```nunjucks
{# comment #}
```

It is also acceptable for C084 to keep comments unsupported and reject them deterministically.

`raw` blocks remain prohibited because they bypass normal template interpretation.

Do not silently accept any unsupported Nunjucks construct merely because the upstream Nunjucks engine understands it.

### R4 — paths and expression types are contract-validated, not just syntactically valid

Validation receives:

```ts
validateResponseTemplateAuthoring(
  template: unknown,
  outputSchema: unknown,
): ResultTemplateValidation
```

Preserve this canonical authoring boundary rather than creating a second UI-only validator.

For every supported path/expression, infer the expression type from the canonical `CommerceResultSchema` plus active loop scope.

Path rules:

- `result.x.y` resolves from the root output schema.
- an active loop alias resolves from that loop collection's item schema.
- a zero-segment `result` interpolation is valid only for a root scalar schema.
- a zero-segment `result` loop source is valid only for a root array schema.
- if the loop item itself is scalar, `{{ item }}` is valid and `{{ item.foo }}` is invalid.
- if the loop item is an object, `{{ item }}` is invalid and scalar descendants / array descendants used by supported expressions are validated recursively.
- arrays may only be consumed as supported `for` collection sources; arrays are not direct scalar interpolation values.
- objects may not be interpolated directly.

Unsafe path segments remain forbidden:

```text
__proto__
prototype
constructor
```

Expression type rules:

```text
string
integer
number
boolean
null literal
```

`integer` and `number` form the numeric type class.

Arithmetic produces numeric output and accepts only numeric operands.

Comparisons produce boolean output. `==` / `!=` require compatible scalar operands (numeric integer/number compatibility is allowed; comparison with `null` is allowed only as a null check). Ordering comparisons require numeric/numeric or string/string operands.

Boolean `and` / `or` / `not` and `if` / `elif` conditions require boolean-valued expressions.

Do not rely on JavaScript/Nunjucks implicit coercion to make an invalid type combination execute.

### R5 — deterministic complexity bounds

Reject a template as `template_too_complex` before rendering if any limit is exceeded:

```text
source UTF-8 bytes     > 8192
parsed template nodes  > 256
nested control-flow depth > 4   # combined supported if/for nesting
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
invalid_template_expression
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

Construct the Environment with an **explicit empty loader list** (or an equivalently proven no-loader configuration). Do not pass `null` / `undefined` for loaders, because Nunjucks interprets an absent loader as permission to install its default loader.

Add a regression that inspects the configured Environment and proves that no loader is installed.

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

If Nunjucks rendering throws, violates the template grammar unexpectedly, encounters division/modulo by zero, or produces output longer than 4096 characters, return the same safe failure semantics used by the current renderer with:

```text
status       = ERROR
code         = INVALID_INPUT
renderedText = responseTemplate.unavailable
```

The low-level Commerce renderer must classify division/modulo-by-zero with a stable bounded internal template-render failure code/message before it is mapped to the existing Tool-result failure. Do not leak an upstream Nunjucks/JavaScript error string.

Do not allow a renderer exception to escape into provider execution or MCP execution, and do not emit `Infinity` or `NaN`.

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

If deterministic generation would exceed any canonical generated-template bound (source bytes, AST node count, loop count or supported control-flow nesting), fail explicitly with `template_generation_too_large`. Do not truncate generated source and do not return a generated template that the canonical validator would reject.

The generator MUST validate its own emitted template through the canonical `validateResponseTemplateAuthoring` boundary before returning it.

Root scalar generation must produce a validator-accepted interpolation of `result`; root array generation must produce a validator-accepted loop over `result`.

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

Migrate C084-owned non-UI fixtures that still produce a final legacy template shape, including:

```text
database/scripts/fixtures/arch020-commerce-capability-cases.mjs
```

C085-owned React/editor/state files and their UI regressions may remain on the old draft shape until COMMERCE-085; do not edit them merely to make the whole repository suite green in C084.

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

- [x] Perform the bounded Result Template ownership/source audit from R11.
- [x] Add direct Nunjucks runtime dependency and lockfile update.
- [x] Replace `ResponseTemplateSchema` with the exact `nunjucks.v1` shape.
- [x] Replace the hand-written delimiter scanner as the canonical syntax authority with installed-Nunjucks parse/AST validation plus Moda's explicit AST allowlist and stable issue codes.
- [x] Validate interpolation, loop and conditional paths against the canonical `CommerceResultSchema`.
- [x] Implement bounded `if`/`elif`/`else`, primitive literals, comparisons, boolean operators, parentheses, numeric arithmetic and unary negation with static expression type inference.
- [x] Add deterministic division/modulo-by-zero render protection without changing the shared Tool-result error contract.
- [x] Enforce source/node/loop/combined-control-depth bounds.
- [x] Add JSON-only/null-prototype render-context sanitization.
- [x] Replace `renderDefinitionResult` text/items branches with the one Nunjucks renderer.
- [x] Add the deterministic provider-neutral default-template generator and prove every generated template passes the canonical validator, including root-scalar/root-array and parallel-loop complexity cases.
- [x] Make publication and current live-Test preflight consume the same canonical validator/renderer.
- [x] Remove obsolete text/items syntax/runtime branches.
- [x] Convert C084-owned Commerce fixtures/tests to `nunjucks.v1`, including `database/scripts/fixtures/arch020-commerce-capability-cases.mjs`; leave C085-owned editor/state fixtures for C085.
- [x] Add bounded security, generation, validation and rendering regressions.

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

- [x] Final Commerce Tool definitions accept only `kind: "nunjucks"`, `runtimeVersion: "nunjucks.v1"` Result Templates.
- [x] Legacy final `text` and `items` templates are rejected; no compatibility runtime branch remains.
- [x] Supported scalar interpolation, bounded `for`/`else`, bounded `if`/`elif`/`else`, primitive literals, comparisons, boolean expressions, parentheses and numeric arithmetic render correctly for their valid schema types.
- [x] Root scalar `{{ result }}` and root-array `{% for item in result %}` are accepted only for matching root schema kinds.
- [x] Unsupported Nunjucks constructs are rejected deterministically before render/provider I/O.
- [x] The canonical validator never accepts source rejected by the installed Nunjucks parser, and Nunjucks parse success alone never bypasses Moda's AST/type allowlist.
- [x] Invalid arithmetic/comparison/boolean operand types fail with deterministic `invalid_template_expression` issues rather than implicit coercion.
- [x] Division/modulo by zero falls back deterministically to `responseTemplate.unavailable` with existing `INVALID_INPUT` Tool semantics and never emits `Infinity`/`NaN`.
- [x] Every interpolated scalar path and every loop collection path is proven against the current canonical result contract.
- [x] No template can access prototype paths, functions, globals, loaders, environment variables, credentials or application service objects; the configured Nunjucks Environment has no loader instance.
- [x] Renderer output remains bounded to 4096 characters and renderer failures fall back without escaping exceptions.
- [x] The deterministic generator produces the exact expected source for the documented `values.items[]` example.
- [x] Generator output is provider-neutral and stable for identical canonical schemas.
- [x] Generator output always passes canonical validation; complexity overflow fails as `template_generation_too_large` rather than returning an invalid template.
- [x] External and Shopify live-Test backends continue to use the production renderer and remain zero-write.
- [x] Publication rejects invalid/incompatible Nunjucks source through the canonical validation boundary.
- [x] No database migration or non-Commerce implementation change is introduced.
- [x] C084-owned non-UI fixtures no longer construct a final `text` / `items` template; C085-owned editor/state migration remains deferred.
- [x] The durable Completion Report records the actual implementation commit, validation results, known C085-owned suite failures and clean dedicated worktree/branch evidence before the task returns to review.

## Validation

- [x] `npx vitest run tests/arch021-commerce-tool-contract.test.ts tests/result-template-authoring.test.ts tests/definition-execution.test.ts`
- [x] `npx vitest run tests/external-http-live-test.test.ts tests/shopify-admin-live-test.test.ts`
- [x] focused generator fixtures for scalar/object/object-list/scalar-list/nested-list schemas
- [x] focused acceptance tests for `if` / repeated `elif` / optional `else`, nested if+for, literals, comparisons, boolean expressions, precedence/parentheses, arithmetic and unary negation
- [x] focused type-matrix rejection tests for string/number/boolean/null misuse and no-coercion behavior
- [x] focused rejection tests for each unsupported construct listed in R3, including calls/method calls/filters/set/macros/import/include/inheritance/bracket/computed access/globals/`loop.*`/raw
- [x] focused rejection tests for unsafe/unknown paths and non-array loop sources
- [x] focused complexity-bound tests for source bytes, AST nodes, loop count and combined if/for nesting depth
- [x] focused renderer tests for Error fallback, empty list `else`, condition branches, optional missing values, division/modulo by zero and 4096-character output bound
- [x] regression proving the Nunjucks Environment has an explicit empty loader set
- [x] generator regressions for root scalar, root array, >16 parallel arrays / >256 generated nodes and self-validation
- [x] focused proof that invalid template preflight causes zero provider I/O in External and Shopify Test
- [x] bounded source audit proving no non-Commerce runtime consumer was silently changed
- [x] source audit proving no C084-owned non-UI fixture still creates legacy final `text` / `items` templates except intentional rejection fixtures
- [x] targeted ESLint for changed files
- [x] changed-file TypeScript diagnostics, or repository typecheck with baseline reconciliation
- [x] `git diff --check`

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not begin COMMERCE-085 or any dependent task.

## Implementation Notes

Do not treat Nunjucks as a sandbox. Moda's security boundary is the combination of a severely restricted accepted grammar, schema-aware path validation, JSON-only/null-prototype context, no loaders/functions/globals and bounded source/result data. If the chosen Nunjucks API cannot support those invariants cleanly, stop and report the concrete incompatibility rather than weakening the language restrictions.

The default generator is an authoring convenience, not a second runtime grammar. It emits ordinary `nunjucks.v1` source that must pass the same canonical validator as user-authored source.

## Completion Report

### Status

Attempt 3 corrections implemented; submitted for architect review. Execution metadata is reconciled to `status: review`, `executor: null` and `claimed_at: null`.

### Files Changed

Commerce implementation commits `161b34d`, `bdc1502` and `5efd2d1` on `task/ARCH-021-COMMERCE-084` contain the AST validator, restricted renderer, generator corrections and focused regressions, and pin database fixture commit `4da3139`. The fixture migration is independently committed and pushed on the matching database task branch. No Shared or C085-owned UI/state file was modified.

### Work Completed

- **Review item 1, amended grammar:** Nunjucks parser/AST is the syntax authority; Commerce applies an explicit AST allowlist, schema-aware expression typing, bounded `for`/`if` control flow, supported literals/operators, and deterministic rejection for unsupported constructs and implicit coercion.
- **Review item 2, loader isolation:** Renderer uses an explicit empty loader list; a regression verifies there are zero loaders, while loading tags remain rejected.
- **Review item 3, generator consistency:** Root scalar/array templates are supported. Every generated template passes `validateResponseTemplateAuthoring`; source, AST-node, loop-count and nesting overflow maps to `template_generation_too_large`.
- **Review item 4, fixture migration:** Migrated `database/scripts/fixtures/arch020-commerce-capability-cases.mjs` to `nunjucks.v1`; Commerce pins database commit `4da3139`.
- **Review item 5, durable handoff:** This report and `status: review` are committed and pushed on the parent task branch. The `## Architect Review` section is intentionally unchanged.
- Division/modulo by zero and non-finite arithmetic receive stable internal codes and bounded messages before mapping to existing `INVALID_INPUT`/unavailable semantics. No `Infinity`/`NaN` output is emitted.
- Preserved the pre-production breaking replacement and canonical publication/Test/production boundary. The bounded R11 ownership audit found no non-Commerce deployable runtime consumer; old local revisions must be re-authored.

### Validation Results

- Attempt 2 focused packet: 10 files, 124 tests passed, covering parser, authoring, generator, renderer, definition execution, External publication/live Test, Shopify Admin authoring validation, Commerce lifecycle and Studio integration.
- Focused renderer suite after conditional branches and stable arithmetic classification: 5 tests passed. Focused generator suite after canonical-boundary self-validation: 5 tests passed.
- Targeted ESLint on changed TypeScript files passed. `git diff --check` passed for Commerce and the nested database repository. `node --check database/scripts/fixtures/arch020-commerce-capability-cases.mjs` passed.
- Attempt 2 `npx tsc --noEmit --pretty false` remains nonzero with 266 repository-wide diagnostics; none reference changed C084 parser, renderer, generator or focused test files.
- Attempt 1 full-suite baseline was 35 failed files, 91 passed and 2 skipped (184 failed tests, 952 passed, 6 skipped, 51 uncaught errors), primarily from C085-owned legacy editor/state assumptions. Full suite was not rerun in Attempt 2.
- Attempt 1 QuickJS preview checks reported worker `MODULE_NOT_FOUND`; disposable C20/MCP suites require PostgreSQL/Redis configuration. Those environment-dependent suites were not rerun in Attempt 2.

### Deviations

Whole-package typecheck remains non-green at the documented 266-diagnostic baseline. Full Commerce Vitest and environment-dependent QuickJS/C20/MCP checks were not rerun. C085-owned UI/state files remain untouched.

### Assumptions

COMMERCE-085 will migrate the editor/state draft assumptions to the strict persisted Nunjucks v1 contract before full UI integration is expected to pass.

### Unresolved Issues

Workspace-wide TypeScript/UI validation still depends on C085 editor/state migration and existing generated-Prisma/baseline fixes. QuickJS preview validation needs its packaged runtime artifact; disposable C20/MCP suites need task-owned PostgreSQL/Redis configuration.

### Architectural Concerns

None identified by the bounded R11 audit. No Shared contract or database migration was introduced.

### Attempt 3 Addendum

#### Corrections

- Equality and inequality now accept only compatible scalar operands, numeric integer/number pairs, or scalar/null checks. Object/object, array/array, object/null and array/null comparisons produce `invalid_template_expression`; scalar optional-null checks remain valid.
- Plain `else` bodies now count the enclosing `if` in combined control depth. An `elif` represented as an `If` continuation remains at the same chain depth. Added regressions for repeated `elif`, four accepted levels, a fifth level through `else`, and a fifth mixed if/for level through `else`.
- Reconciled every Work Item, Acceptance Criterion and Validation checkbox against the recorded implementation and evidence. The complete Architect Review history is preserved unchanged.

#### Attempt 3 Files and Validation

- Commerce implementation commit: `421c02dd692664bb435abdcc7a25b5856a29cc62`, pushed to `origin/task/ARCH-021-COMMERCE-084`; it changes only `src/commerce/tool-authoring/nunjucks-template.ts` and `tests/nunjucks-template.test.ts`.
- Focused 10-file packet: 125 tests passed. Required contract/authoring/execution and External/Shopify live-Test packet: 4 files, 56 tests passed. Parser regression suite: 7 tests passed. Targeted ESLint and Commerce/database `git diff --check` passed.
- Repository `tsc --noEmit --pretty false` remains nonzero with 266 errors, matching the Attempt 2 baseline count; no diagnostics reference either changed file. Full Commerce suite and environment-dependent QuickJS/C20/MCP checks were not rerun; prior documented blockers remain.

#### Attempt 3 Execution Evidence

- Launcher-resolved parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-084`; Commerce implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-084`; nested database worktree: Commerce `database/`.
- At attempt start the parent task branch was `a311e8feb5521d834722bcf4529fb393e67f8e2a`; the launcher reported task branches already current with `origin/main`, no fast-forward required. Commerce started at `5efd2d1eaad7941d4e8230d29eeacbfdfd7f5905`. The launcher verified recursive submodule initialization at database commit `4da313921d9521c23058722188e2802f7fbf7779`.
- Commerce Attempt 3 commit and remote task-branch tip match at `421c02dd692664bb435abdcc7a25b5856a29cc62`. Database local and remote task-branch tips match at `4da313921d9521c23058722188e2802f7fbf7779`. Commerce and database worktrees were clean after publication. Parent task report is now committed and pushed on its mirrored task branch; local and remote parent tips were verified equal.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 2 is not accepted.

The five Attempt 1 correction areas are substantially implemented correctly:

- the installed Nunjucks parser/AST is now the syntax authority and Moda applies its own bounded AST/type allowlist;
- bounded `if`/`elif`/`else`, primitive literals, comparisons, boolean expressions, parentheses, arithmetic and unary negation are present;
- the renderer uses an explicit empty loader list and the focused regression proves zero loaders;
- root scalar/root array generation is supported and every generated template is self-validated through the canonical authoring validator;
- division/modulo-by-zero and non-finite arithmetic map safely to the existing `INVALID_INPUT` / unavailable Tool-result semantics;
- the C084-owned ARCH-020 fixture is migrated to `nunjucks.v1`; and
- the Completion Report is now durably present in the submitted snapshot.

Two task-scoped semantic defects remain in the canonical validator, followed by one durable task-record correction.

#### 1. Equality/inequality currently accepts non-scalar object/array operands

R4 requires:

```text
== / != require compatible scalar operands
comparison with null is allowed only as a scalar null check
```

`compatibleComparison(...)` currently implements equality as:

```ts
return (
  left === right ||
  left === "null" ||
  right === "null" ||
  numericTypes.has(left) && numericTypes.has(right)
);
```

Because `ExpressionType` also contains `array` and `object`, this accepts unsupported expressions such as:

```nunjucks
{% if result.values.items == result.values.items %}
{% if result.values.product == result.values.product %}
{% if result.values.items != null %}
{% if result.values.product == null %}
```

Those are not compatible scalar comparisons and must fail canonical validation with:

```text
invalid_template_expression
```

Attempt 3 must restrict `==` / `!=` to:

- same compatible scalar type;
- numeric `integer` / `number` compatibility; and
- scalar-vs-`null` (or `null`-vs-`null`) null checks.

Arrays and objects must never be comparison operands in `nunjucks.v1`, including comparisons to `null`.

Add focused regressions for object/object, array/array, object/null and array/null equality/inequality rejection while preserving scalar null checks such as:

```nunjucks
{% if result.values.optionalName == null %}
```

#### 2. Nested control-flow depth is under-counted inside a plain `if ... else` branch

R5 bounds the **combined supported if/for nesting depth** to 4.

`validateIf(...)` currently validates its normal body at:

```ts
controlDepth + 1
```

but calls:

```ts
validateBranch(node.else_, controlDepth)
```

for the else side.

`validateBranch(...)` then passes that unchanged depth into a plain else `NodeList`. As a result, controls nested inside a normal `else` body do not count the enclosing `if`.

A shape equivalent to:

```nunjucks
{% if result.values.active %}
{% else %}
  {% if result.values.hidden %}
    {% if result.values.active %}
      {% if result.values.hidden %}
        {% if result.values.active %}
          too deep
        {% endif %}
      {% endif %}
    {% endif %}
  {% endif %}
{% endif %}
```

can therefore be under-counted relative to the canonical depth-4 limit.

Attempt 3 must distinguish:

- an `elif` represented by Nunjucks as an `If` in `else_`, which remains at the same logical if-chain depth; from
- a plain `else` body, whose nested controls must be validated at `controlDepth + 1`.

Add focused regressions proving:

- repeated `elif` clauses do not artificially increase nesting depth;
- a control nested inside an `else` counts the enclosing `if`; and
- a fifth combined if/for level reached through an else branch deterministically produces `template_too_complex`.

Do not change the canonical depth limit.

#### 3. Reconcile the durable execution-owned task record before resubmission

The submitted task is `status: review`, but the authoritative task record still contains:

```text
executor: copilot
claimed_at: <non-null>
```

and every Work Item, Acceptance Criterion and Validation checkbox remains unchecked even though the Completion Report says the work was performed.

Under the repository-task protocol those fields/checklists are implementing-agent-owned execution state and must be reconciled before review.

Attempt 3 must:

- claim the task normally, incrementing `attempt` from 2 to 3;
- check every Work Item actually completed;
- check every Acceptance Criterion actually satisfied;
- check every required Validation item actually executed;
- leave any genuinely unavailable validation unchecked and explain it in the Completion Report;
- record the launcher-resolved parent/Commerce/database physical worktree paths, start-of-attempt synchronization evidence, relevant recursive submodule/database evidence, pushed commit tips and clean-worktree evidence in the Completion Report;
- return with `status: review`, `executor: null`, `claimed_at: null`; and
- preserve the full Attempt 1/2 Architect Review history.

The user handoff states that the branches are pushed and clean; the durable Completion Report must contain the corresponding evidence rather than relying on chat history.

No C085 UI/state implementation is requested.

### Reviewed Files

- `src/commerce/tool-authoring/nunjucks-template.ts`
- `src/commerce/tool-authoring/result-template-contract.ts`
- `src/commerce/tool-authoring/result-template-generator.ts`
- `src/commerce/execution/renderer.ts`
- `src/commerce/tool-definition/result-schema.ts`
- `tests/nunjucks-template.test.ts`
- `tests/result-template-authoring.test.ts`
- `tests/result-template-generator.test.ts`
- `tests/result-template-renderer.test.ts`
- `database/scripts/fixtures/arch020-commerce-capability-cases.mjs`
- C084 Completion Report — Attempt 2

### Validation Reviewed

Submitted Attempt 2 evidence:

- focused packet: 10 files, 124 tests passed;
- contract/authoring/execution/live-Test subset: 67 tests passed;
- targeted ESLint: passed;
- changed-file diagnostics: clean;
- Commerce/database `git diff --check`: passed;
- migrated fixture `node --check`: passed;
- repository-wide TypeScript remains non-green with 266 unrelated diagnostics, none in changed C084 files;
- full suite and environment-dependent QuickJS/C20/MCP checks were not rerun and remain documented limitations.

These broader baseline/environment limitations are not the reason for this review outcome.

Source inspection confirms the Attempt 1 no-loader, generator self-validation/root handling, fixture migration and expanded AST/type-aware grammar corrections. Acceptance is blocked only by the two validator semantics above and the unreconciled durable task execution record.

### Architecture Conformance

Partial.

The canonical one-runtime/one-renderer architecture, restricted Nunjucks environment, JSON-only context, publication/Test/production convergence, expanded bounded expression grammar, provider-neutral generator and pre-production breaking migration now conform.

The remaining deviations are:
1. non-scalar equality/null comparisons are accepted contrary to R4;
2. plain `if ... else` control depth is under-counted contrary to R5; and
3. the task has not completed the required durable execution-state/checklist/worktree reconciliation.

### Follow-up

Return the same task as Attempt 3.

Correct only the comparison-type and else-depth semantics above, add the focused regressions, reconcile the execution-owned task record/evidence, rerun the focused validator packet plus required changed-file checks, and STOP.

Do not implement COMMERCE-085 in C084.

COMMERCE-085 remains Pending on C084, and COMMERCE-083 remains Pending on C085.
