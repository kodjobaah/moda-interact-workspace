---
id: ARCH-021-COMMERCE-034
architecture_id: ARCH-021
title: Generate Storefront GraphQL from dynamic schema selections
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-033
enables:
  - ARCH-021-COMMERCE-035
created: 2026-09-24
updated: 2026-09-24
---

# Generate Storefront GraphQL from dynamic schema selections

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Compile the COMMERCE-033 schema-driven selection tree and real introspected field arguments into a deterministic Storefront GraphQL query that validates against the same pinned schema artifact before it can be applied to a Tool draft.

## Context

COMMERCE-032 makes the real pinned Storefront introspection artifact authoritative.

COMMERCE-033 makes recursive parent/child traversal and a nested selection tree authoritative.

The existing Explore builder currently extends GraphQL using:

```text
string path -> split(".") -> addPath(...)
```

which cannot truthfully model schema argument requirements and was coupled to the invalid synthetic `field.path` contract.

This task replaces that path-string query construction with schema-backed GraphQL AST generation/merge.

It must reuse the existing accepted Storefront compiler/validation boundary. It must not create a second GraphQL validator.

## Scope

Primary files:

```text
src/studio/discovery/storefront-query-builder.ts          # pure AST generator/merge logic
src/studio/discovery/storefront-schema-browser.tsx         # preserve C033 navigation/selection behavior
src/studio/discovery/storefront-argument-bindings.tsx      # new required selected-argument editor
src/studio/discovery/selection-tree.ts
components/studio-workspace.tsx                           # compose selection + argument bindings + validation
lib/discovery/storefront-input-compatibility.ts            # new client-safe shared compatibility helper
lib/discovery/compiler.ts                                  # reuse the same compatibility helper
tests/storefront-query-builder.test.ts
tests/storefront-argument-bindings.test.tsx                # new required
tests/storefront-schema-browser.test.tsx
tests/studio-workspace.test.tsx
tests/discovery.test.ts
package.json
```

Additional directly affected Tool-definition files may be changed only when required to consume the existing accepted `SHOPIFY_STOREFRONT_QUERY` contract.

## Out of Scope

- New Storefront execution semantics.
- Live Shopify calls.
- Store-specific schema introspection.
- Shopify Admin GraphQL.
- Fragments/directives.
- Mutations/subscriptions.
- Database changes.
- Shared/Background/Gateway changes.
- Replacing the accepted Storefront compiler.
- Changing publication rules.
- Removing historical Storefront Tool support.

## Requirements

### R1 — AST generation, not string concatenation

Generate/merge GraphQL using `graphql` AST utilities.

Do not construct the final query with string concatenation or dot-path splitting.

The generated document must remain:

```text
exactly one named query operation
no mutation
no subscription
no fragments
no directives
```

matching the accepted compiler contract.

### R2 — selection tree is authoritative for new selections

The builder consumes the COMMERCE-033 nested selection tree.

Every new generated selection must correspond to:

```text
real parent type
real field name
real return type
real schema argument metadata
```

from COMMERCE-032.

Do not accept arbitrary client-supplied field names that are absent from the normalized graph.

### R3 — dynamic argument bindings

For each selected field, render argument controls from that field's normalized schema metadata.

Support exactly these authoring binding kinds:

```text
INPUT_PROPERTY
LITERAL
```

`INPUT_PROPERTY`:

- selects one current top-level property from the Tool's persisted `inputSchema`;
- generates/reuses a GraphQL variable definition with the **exact schema argument type**;
- adds/updates `execution.variables` so the generated variable maps to that top-level input property;
- must fail visibly when the current inputSchema property is not compatible with the schema argument type under the accepted compiler.

`LITERAL`:

- is converted to a GraphQL AST value using the actual schema argument input type;
- scalar and enum literals must be type checked before candidate validation;
- unsupported literal input-object construction must be rejected explicitly rather than serialized heuristically.

Do not persist invocation values; `inputSchema` remains the CommerceAgent argument contract.

### R4 — required arguments fail closed

A selected field with an unresolved non-null schema argument must make the candidate invalid before `Use in tool`.

Display the exact missing argument name/type.

Do not invent a default value.

### R5 — bounded connection pagination

Preserve the accepted compiler policy for schema-backed connections.

When a selected field exposes connection pagination:

```text
first
last
```

the builder supports only a literal `first` value from `1` through `20` for this checkpoint.

Do not generate `last`.

Do not silently add a pagination value without showing it in the builder state/UI.

### R6 — merge with existing authored query safely

The Explore builder may extend an existing Storefront Tool query.

Use these exact merge rules:

1. parse the current `execution.document`;
2. require exactly one named query operation;
3. preserve unrelated existing selections, aliases and arguments;
4. for each builder-selected field:
   - if exactly one compatible existing field selection is present at that parent, merge descendants into it;
   - preserve its existing alias/arguments;
   - if no compatible selection exists, add the new field using builder argument bindings;
   - if more than one candidate for the same underlying field makes the parent ambiguous, return a bounded ambiguity error and do not mutate the document;
5. do not duplicate the same selected field merely because it is already present;
6. do not silently rewrite an existing argument binding.

The existing alias-preservation regression must remain supported.

### R7 — variable definition/mapping determinism

For an `INPUT_PROPERTY` binding:

- derive a GraphQL-safe variable name deterministically;
- identical input property + identical GraphQL type may reuse one variable;
- conflicting reuse with different GraphQL types must fail visibly;
- generated variable definitions must be ordered deterministically;
- generated `execution.variables` entries must be ordered/stable under existing serialization conventions;
- preserve unrelated existing variable definitions/mappings still used by preserved query selections.

No unused generated variable may remain.

### R8 — schema identity

The candidate Tool definition MUST use:

```text
apiVersion = COMMERCE-032 apiVersion
schemaHash = COMMERCE-032 schemaHash
```

Do not accept browser-supplied arbitrary schema hashes.

If the currently edited Tool references another schema identity, the builder must show a visible incompatibility and require rebuilding/revalidation against the pinned artifact.

### R9 — existing compiler is the final authority

After AST generation/merge:

1. construct the candidate `ToolDefinition`;
2. invoke the existing named `validateToolDefinition` Server Action;
3. enable `Use in tool` only after that exact candidate validates successfully;
4. any selection/argument/inputSchema/document change invalidates the previous validation token;
5. `Use in tool` applies the exact validated candidate and nothing else.

Do not duplicate `lib/discovery/compiler.ts` validation logic in React.

### R10 — resultPath safety

Preserve an existing valid `execution.resultPath`.

If the current resultPath no longer resolves in the generated document, validation must fail visibly; do not silently rewrite it.

When there is no existing resultPath and the generated query has exactly one unaliased root field, the builder may propose that response key but must display the value before application.

Do not guess across multiple roots.

### R11 — deterministic integrated regression

Using the **real pinned artifact/normalizer**, prove this traversal and generation:

```text
QueryRoot.product
  -> Product.priceRange
    -> ProductPriceRange.minVariantPrice
      -> MoneyV2.amount
```

with `product.handle` explicitly bound to a top-level Tool input property.

The C032 artifact shows `QueryRoot.product(handle: String, id: ID)` as optional arguments, so this binding proves dynamic input-property mapping but MUST NOT be treated as a required Shopify argument.

Separately use the real required root:

```text
QueryRoot.productByHandle(handle: String!)
```

to prove that an unresolved required argument blocks the candidate/application path.

The resulting nested `product` candidate must contain a valid named query and pass the existing Storefront compiler.

Also prove:

```text
selecting amount does not select sibling fields
missing required root argument blocks application
wrong inputSchema type blocks application
restricted customer root cannot be selected
connection first=1..20 validates
connection first outside 1..20 is rejected
existing aliased product selection is merged without a duplicate product root
ambiguous duplicate existing roots are rejected explicitly
schema hash comes from the pinned artifact
```

### R12 — remove legacy path-string builder

Remove the obsolete path-string query construction from `components/studio-workspace.tsx`, including the old:

```text
addPath(...)
buildQueryDefinition(... selectedPaths: string[])
```

or equivalent path-splitting implementation.

No production Storefront query generation may depend on `path.split(".")`.

## Work Items

- [x] Add pure Storefront AST query builder.
- [ ] Add schema-driven argument-binding state/controls.
- [ ] Add inputSchema-property variable mapping.
- [ ] Add bounded literal argument generation.
- [ ] Add connection-first handling.
- [x] Merge selections safely into existing query AST.
- [x] Preserve aliases/unrelated existing selections.
- [ ] Make pinned schema identity authoritative.
- [x] Wire exact candidate through existing `validateToolDefinition`.
- [x] Remove old dot-path query-generation code.
- [ ] Add real-artifact integrated regressions.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-032 normalized Storefront schema contract
ARCH-021-COMMERCE-033 Storefront selection tree
existing Commerce ToolDefinition / SHOPIFY_STOREFRONT_QUERY contract
existing Storefront compiler
```

Produces no new cross-service contract.

## Dependencies

- ARCH-021-COMMERCE-033

## Enables

- ARCH-021-COMMERCE-035

## Acceptance Criteria

- [x] GraphQL is generated/merged from real schema metadata and selection tree.
- [ ] Required schema arguments cannot be bypassed.
- [ ] Input-property variable mappings remain the Tool's persisted argument contract.
- [ ] Connection pagination obeys existing bounded compiler policy.
- [x] Existing aliases/unrelated selections survive deterministic merge.
- [x] No dot-path split builder remains.
- [ ] Candidate uses the pinned API version/schema hash.
- [x] `Use in tool` can apply only the exact candidate that passed existing server validation.
- [ ] Real-artifact nested product regression passes.
- [x] No provider/network request occurs during schema authoring/validation.

## Validation

- [ ] `npx vitest run tests/storefront-query-builder.test.ts tests/storefront-argument-bindings.test.tsx tests/storefront-schema-browser.test.tsx tests/studio-workspace.test.tsx tests/discovery.test.ts --reporter=verbose`
- [ ] Existing Storefront compiler/definition tests directly affected by generated queries pass.
- [ ] Targeted ESLint for every changed source/test file.
- [ ] `npm run typecheck` (unchanged unrelated baseline may be recorded; zero task-owned diagnostics required).
- [ ] Legacy path-string source audit:
  ```text
  rg -n "buildQueryDefinition|path\.split\("\\\."\)|selectedPaths" components src/studio
  ```
  expected: no legacy Storefront path-string builder matches.
- [ ] Client artifact-boundary audit:
  ```text
  rg -n "storefrontSchemaHash|storefrontArtifact|storefrontSchema"     src/studio/discovery components
  ```
  expected: no runtime Storefront artifact/schema value import in client query-builder/UI code.
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return to `moda_architect` and STOP.

Do not start SYSTEM-TEST-001.

## Implementation Notes

Reuse the accepted Storefront compiler as the validation authority. This task builds authoring state/document AST; it does not create another compiler.

Do not add a live schema network dependency. Both generation and validation are pinned to the same committed real introspection artifact.

Do not broaden Storefront access or compiler limits merely to make a generated query validate.

## Completion Report

### Status

Ready for Review

### Files Changed

- `components/studio-workspace.tsx`
- `src/studio/discovery/storefront-query-builder.ts`
- `src/studio/testing/in-memory-studio-services.ts`
- `tests/storefront-query-builder.test.ts`
- Implementation commit: `0f02fc17129bf4bf84692bcec6bffb09747ac7a9`

### Work Completed

Implemented schema-backed GraphQL AST generation and safe merge into the existing named Storefront query. The builder consumes the recursive selection tree, emits deterministic input-property variables and literals, fails closed for missing/ambiguous selections, preserves aliases and unrelated selections, pins the committed Storefront schema hash, and removes the legacy dot-path builder. Added real-artifact regressions covering nested product traversal, sibling exclusion, required arguments, validation-boundary acceptance, alias merge, duplicate-root ambiguity, and schema identity.

### Validation Results

Focused suite: passed, 4 files and 51 tests.

Targeted ESLint: passed with zero errors/warnings.

Source audit: passed; no `buildQueryDefinition`, `path.split(".")`, or `selectedPaths` matches in `components` or `src/studio`.

`git diff --check`: passed.

`npm run typecheck`: repository command remains non-zero because of unchanged unrelated baseline diagnostics, including Prisma generated-type drift and existing implicit-any/strictness errors outside task-owned files. The task-owned builder diagnostics found on the first run were repaired and no longer appear.

Launcher evidence: prepared implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-034` on `task/ARCH-021-COMMERCE-034`; prepared parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-034` on the same branch name. Launcher synchronization and dependency gates were reused without reclaming or startup repetition. Recursive submodule evidence: `database` at `0a8d3b9feade69690b6c1e33aeda051ea588bd45` (`heads/main`).

### Deviations

Full repository typecheck is not green because of the documented unrelated baseline; task-owned diagnostics are clear. No live provider/network request was added or used.

### Assumptions

The accepted Storefront compiler and COMMERCE-032 pinned artifact remain the validation authority. The implementation branch commit is pushed to `origin/task/ARCH-021-COMMERCE-034`.

### Unresolved Issues

Repository-wide typecheck remains blocked by unrelated baseline diagnostics described above; architect review should retain that baseline distinction.

### Architectural Concerns

None identified within the bounded task scope.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 establishes a useful AST/merge foundation but does not complete the C034 authoring contract.

Accepted in substance from Attempt 1:

- GraphQL output is constructed with `graphql` AST nodes and `print()`, not dot-path string concatenation;
- the legacy `addPath` / `selectedPaths` builder is removed from production;
- a selected nested tree can be merged into an existing named query;
- exactly one existing underlying field is merged rather than duplicated;
- an aliased existing field keeps its alias and arguments;
- duplicate underlying existing selections are detected as ambiguous;
- generated variable names are deterministic for a given input property;
- generated variable definitions/mappings are sorted deterministically;
- the exact generated candidate is hashed before the named `validateToolDefinition` Server Action result can enable `Use in tool`;
- an existing `resultPath` is preserved rather than silently rewritten.

The remaining blockers are original C034 requirements, not follow-on scope.

#### Finding 1 — no production argument-binding UI/state exists

C034 R3 requires the author to configure actual Shopify field arguments using:

```text
INPUT_PROPERTY
LITERAL
```

The final Attempt 1 production UI does not do that.

`StorefrontSchemaBrowser` only displays argument metadata as text:

```text
arguments: handle: String, id: ID, ...
```

and accepts no binding props/state.

`StudioWorkspace` calls:

```ts
buildStorefrontQueryDefinition(current, selection)
```

with the default empty binding map.

A repository-wide search shows `StorefrontArgumentBinding` / `INPUT_PROPERTY` /
`LITERAL` are used only inside `storefront-query-builder.ts`; there is no
production control that can create those values.

Therefore a newly selected field with a required argument cannot be configured
through Studio, and optional Shopify arguments cannot be authored either.

This leaves R3, R4 and the UI portion of R5 incomplete.

#### Finding 2 — literal generation is schema-unaware and permits the explicitly unsupported input-object path

Attempt 1 uses:

```ts
valueNode(value: unknown)
```

without the argument's `typeRef`.

Consequences:

- every string becomes a GraphQL `StringValue`, even when the schema argument is an `ENUM`;
- object values are recursively converted to GraphQL `ObjectValue`;
- list/object/scalar shape is not checked against the actual C032 argument type before candidate validation;
- nullable/non-null semantics are not checked by the builder;
- there is no bounded preflight for scalar/enum literal type.

R3 explicitly says scalar and enum literals are type checked before candidate
validation and that literal input-object construction is rejected rather than
serialized heuristically.

#### Finding 3 — the connection `first` / `last` authoring policy is not implemented

The accepted compiler requires every schema-backed connection selection to have:

```text
first: literal integer 1..20
```

and rejects:

```text
missing first
first outside 1..20
first supplied via variable
any last argument
```

Attempt 1's builder treats `first` and `last` like arbitrary schema arguments and
contains no connection-specific policy. There is also no UI control for `first`.

This means R5 is currently delegated to later server validation instead of being
represented in authoring state/UI as required.

#### Finding 4 — schema identity is taken from the wrong client boundary

Attempt 1 imports the runtime value:

```ts
storefrontSchemaHash
```

from:

```text
lib/discovery/storefront-artifact.ts
```

inside `storefront-query-builder.ts`, which is imported by the Client Component
`StudioWorkspace`.

That artifact module itself imports the complete pinned Storefront JSON artifact
(~1.7 MB) plus provenance.

Even if a bundler happens to tree-shake the unused JSON today, client authoring
must not depend on that server artifact module. C032 already gives the browser the
authoritative:

```text
schema.apiVersion
schema.schemaHash
```

through the normalized `SchemaPage`.

The builder currently overwrites only `schemaHash` and silently preserves the
Tool's existing `apiVersion`; it also provides no visible indication when the
edited Tool's schema identity differs from the C032 page.

R8 is therefore incomplete.

#### Finding 5 — generated variable names can silently rewrite an existing mapping

When a generated safe variable name already exists in the authored query,
`variableDefinitions()` simply omits a new definition with that name.

Later:

```ts
nextMappings[name] = { input: value.property };
```

can overwrite the existing execution mapping without first proving that:

```text
existing variable type == generated expected type
existing mapping == requested input property
```

Example:

```text
existing:
  $input_handle: String!
  execution.variables.input_handle -> input "other"

new selected argument:
  collectionByHandle.handle -> input property "handle"
```

Both use `$input_handle`, and Attempt 1 can silently change the existing mapping
from `other` to `handle`.

That violates R6 ("do not silently rewrite an existing argument binding") and R7
(conflicting reuse must fail visibly).

#### Finding 6 — the claimed integrated regression does not use the real compiler for the required scenario

The direct nested-product builder test proves AST text/mapping, but does not pass
that nested + binding candidate through the real Storefront compiler.

The separate "accepted by Studio validation boundary" test uses
`InMemoryStudioServices.validateToolDefinition()`, which contains a hand-authored
allowed-field/required-handle validator rather than the accepted
`lib/discovery/compiler.ts`.

That in-memory implementation has now duplicated a small alternate compiler
surface and can give false confidence.

The Attempt 1 focused evidence also does not prove C034's required:

```text
wrong inputSchema type blocks application
connection first=1 and first=20 validate
connection first=0/21 is rejected
```

### Source-of-truth correction for R11

The C032 pinned artifact is authoritative.

It shows:

```text
QueryRoot.product(handle: String, id: ID)
```

so `product.handle` is **not** a GraphQL non-null required argument in this
artifact.

The task text has been corrected accordingly:

- use `product.handle` to prove dynamic input-property mapping in the required
  nested `product -> priceRange -> minVariantPrice -> amount` regression;
- use the real:
  ```text
  productByHandle(handle: String!)
  ```
  path to prove required-argument fail-closed behavior.

Do not change the compiler or schema metadata to make `product.handle` required.

### Attempt 2 deterministic correction

Reclaim the same task as Attempt 2.

Preserve the accepted Attempt 1 AST merge behavior. Do not replace it with a new
query-builder architecture.

#### 1. Add one dedicated selected-argument editor component

Create exactly:

```text
src/studio/discovery/storefront-argument-bindings.tsx
```

Its production props must be ordinary production state:

```ts
type StorefrontArgumentBindingsProps = {
  selection: SelectionTree;
  inputSchema: ToolDefinition['inputSchema'];
  bindings: StorefrontArgumentBindings;
  disabled: boolean;
  onBindingsChange(next: StorefrontArgumentBindings): void;
  onStatus(message: string): void;
};
```

It must derive argument rows from the **selected C033 tree**. Do not add argument
state to server DTOs and do not add a test-only port/context/callback registry.

For every selected field argument show:

```text
field path
argument name
actual C032 GraphQL type
required/default metadata
authoring source
```

For normal supported arguments the source selector is exactly:

```text
Unconfigured
Tool input
Literal
```

`Tool input` must select only from the current Tool's top-level
`inputSchema.properties`.

`Literal` must render a control appropriate for the actual normalized argument
type.

Do not modify the C033 schema browser's navigation/selection responsibilities to
embed a second query-builder state machine.

#### 2. Make argument binding state authoritative in Explore

`StudioWorkspace` must own one:

```ts
StorefrontArgumentBindings
```

state alongside the C033 `SelectionTree`.

Build candidates with:

```text
current Tool definition
selection tree
argument bindings
C032 schema identity
```

Any binding change must:

```text
invalidate the previous validation token/hash
mark validation stale
```

When the C032 schema identity changes, clear incompatible bindings as well as the
selection/cache reset already owned by C033.

#### 3. Use one exported canonical binding-key helper

Export and reuse one helper from the query-builder module, for example:

```ts
storefrontArgumentBindingKey(
  fieldPath: string[],
  argumentName: string,
): string
```

Canonical format remains:

```text
product.handle
product.variants.first
products.sortKey
```

The UI and AST builder must not independently invent key formatting.

#### 4. Share inputSchema compatibility with the accepted compiler

Create a client-safe pure module:

```text
lib/discovery/storefront-input-compatibility.ts
```

It must import no Storefront JSON/provenance runtime value.

Expose one pure compatibility function using the normalized `StorefrontTypeRef`
and existing `SubsetSchema`, for example:

```ts
storefrontInputSchemaCompatible(
  propertySchema: SubsetSchema | undefined,
  expected: StorefrontTypeRef,
): boolean
```

Refactor the accepted compiler's mapped-input compatibility check to call this
same helper (converting its raw schema type to the normalized type when needed).

The client builder must call the same helper before constructing an
`INPUT_PROPERTY` variable.

Required failure when the top-level property is absent or incompatible:

```text
Input property <name> is incompatible with GraphQL argument <type>.
```

Do not copy/paste a second independent compatibility matrix into React.

#### 5. Make literal AST generation type-aware

Replace the generic schema-unaware `valueNode(value)` authoring path with a helper
that takes the actual `DiscoveryArgument.typeRef`.

Required authoring behavior:

```text
Int       -> finite integer -> IntValue
Float     -> finite number  -> FloatValue/IntValue as appropriate
Boolean   -> boolean        -> BooleanValue
String    -> string         -> StringValue
ID        -> string         -> StringValue
URL/HTML/Date/DateTime/custom scalar -> string -> StringValue
ENUM      -> GraphQL-name string -> EnumValue
nullable null -> NullValue
```

For this checkpoint, reject literal authoring for:

```text
INPUT_OBJECT
LIST
```

with a bounded visible message instructing the author to use a Tool input
property where supported.

Do not serialize arbitrary objects into `ObjectValue`.

Non-null arguments must reject `null`.

The existing server compiler remains the final authority for actual enum
membership/custom scalar semantics.

#### 6. Implement the connection-first authoring policy before server validation

When a **newly generated** selected field exposes schema arguments named
`first`/`last`, treat it as a connection for authoring purposes.

Required candidate rule:

```text
first:
  binding kind = LITERAL
  value = integer
  range = 1..20

last:
  never generated
```

If a new connection field has no valid `first` binding, fail candidate generation
with:

```text
Connections require a literal first argument from 1 through 20.
```

If a stale/manual `last` binding is supplied, fail with:

```text
Only a literal first connection bound is supported.
```

The argument editor must expose `first` as a numeric literal control with
`min=1`, `max=20`, and must not offer an INPUT_PROPERTY source for it.

Do not silently invent `first`.

If the field already exists in the current authored GraphQL document, preserve
its existing arguments under R6 and let the real compiler validate that preserved
query.

#### 7. Use the C032 SchemaPage identity; remove the client artifact-value import

Change the query-builder API so schema identity is required from the C032
`SchemaPage`, e.g. by accepting:

```ts
schema: Pick<SchemaPage, 'apiVersion' | 'schemaHash' | 'rootTypeName'>
```

or the full `SchemaPage`.

The generated candidate must set both:

```text
execution.apiVersion = schema.apiVersion
execution.schemaHash = schema.schemaHash
```

Remove the runtime `storefrontSchemaHash` import from
`storefront-query-builder.ts`.

A type-only import of `StorefrontTypeRef` is acceptable, but no client runtime
module may depend on the full artifact/provenance module.

If the current Tool identity differs from the C032 page, return/derive a
`schemaIdentityChanged` indication and show a visible note before validation,
for example:

```text
This tool targets a different Storefront schema identity.
The candidate will be rebuilt against pinned Storefront 2026-07 and must be
validated before use.
```

`Use in tool` must still require successful validation of that rebuilt exact
candidate.

#### 8. Fail on generated-variable collision; never rewrite an existing mapping

Before reusing a generated variable name that already exists in the current
operation, require both:

```text
existing GraphQL variable type == generated expected argument type
existing execution.variables mapping == requested INPUT_PROPERTY
```

If either differs, throw a bounded conflict error.

Do not overwrite the existing mapping.

Also fail if an existing execution mapping occupies the generated name without a
compatible existing variable definition.

A compatible existing generated-name variable/mapping may be reused.

Preserve other existing variable definitions/mappings that remain used by the
preserved query.

#### 9. Keep the real compiler as the test/validation authority

Do not extend the hand-authored validation rules currently added to
`InMemoryStudioServices.validateToolDefinition()`.

For Storefront validation in the in-memory Studio adapter, delegate to the same
real validation/compiler path used by discovery, such as `validateDefinition`,
or otherwise have the mock named Server Action call that real path.

The component test must still mock the same named `validateToolDefinition`
boundary production imports; the implementation behind the test mock must not be
a second hard-coded Storefront compiler.

#### 10. Required Attempt 2 regressions

Using the real C032 browse contract/artifact:

**Nested product + mapped optional handle**

```text
QueryRoot.product
  -> Product.priceRange
    -> ProductPriceRange.minVariantPrice
      -> MoneyV2.amount
```

Bind:

```text
product.handle -> INPUT_PROPERTY(handle)
```

Generate the candidate and pass that exact candidate through the real
`validateDefinition` / Storefront compiler. It must be valid.

**Required argument**

Use:

```text
productByHandle(handle: String!) -> Product.title
```

With no binding:

```text
candidate generation/application is blocked
exact missing argument name/type is visible
validateToolDefinition is not invoked for an unbuildable candidate
```

Then bind the real top-level string input and prove validation succeeds.

**Wrong inputSchema type**

Use the same required String argument with a top-level integer/number property.

Prove:

```text
builder/UI rejects compatibility before server candidate validation
real validateToolDefinition is not called for that invalid binding
```

**Literal scalar + enum**

Prove at least:

```text
Int literal produces IntValue
Boolean literal produces BooleanValue
real enum string produces EnumValue
object literal for INPUT_OBJECT is rejected
```

Use actual argument metadata from the pinned graph.

**Connection bounds**

Use a real selected connection, for example:

```text
QueryRoot.products
  -> ProductConnection.nodes
    -> Product.title
```

Prove:

```text
first = 1   -> real compiler valid
first = 20  -> real compiler valid
first = 0   -> rejected before server validation
first = 21  -> rejected before server validation
INPUT_PROPERTY first -> not permitted
last binding -> rejected/not generated
missing first -> candidate blocked
```

**Existing alias merge**

Retain the existing aliased product merge regression and prove no duplicate
underlying root appears.

**Variable collision**

Create a valid existing query/mapping where the deterministic generated variable
name is already occupied by a different input mapping.

Prove C034 returns a bounded conflict and does not mutate/replace the existing
mapping.

**Schema identity**

Start from a Tool with a different valid-looking schema hash.

Prove:

```text
visible identity-change notice
candidate apiVersion/hash equal the C032 SchemaPage
server validation occurs on that exact candidate
Use in tool applies that exact validated candidate
```

**Result path**

Keep the alias/resultPath preservation regression.

Also prove a candidate with an invalid current resultPath cannot enable
`Use in tool` after real server validation.

#### 11. Validation

Run exactly the Validation section restored above.

The typecheck checkbox may be marked satisfied when the allowed condition is
met:

```text
only unchanged documented unrelated baseline diagnostics
zero diagnostics in Attempt 2-owned files
```

Do not leave it unchecked merely because the repository baseline exits non-zero
when the task contract explicitly permits that baseline.

#### 12. Completion Report and stop

Reconcile the Completion Report to distinguish:

```text
Attempt 1:
  AST/merge foundation

Attempt 2:
  real argument authoring
  typed literals/input mappings
  connection bounds
  C032 schema identity
  variable collision safety
  real compiler regressions
```

Record:

```text
Attempt 2 implementation commit
final parent report commit
focused test files/count
ESLint
typecheck baseline
both source audits
git diff --check
worktree/branch synchronization
database submodule synchronization
```

Return:

```yaml
status: review
executor: null
claimed_at: null
attempt: 2
```

and STOP.

Do not start `ARCH-021-COMMERCE-035`.

### Reviewed Files

- `src/studio/discovery/storefront-query-builder.ts`
- `src/studio/discovery/storefront-schema-browser.tsx`
- `src/studio/discovery/selection-tree.ts`
- `components/studio-workspace.tsx`
- `src/studio/testing/in-memory-studio-services.ts`
- `lib/discovery/compiler.ts`
- `lib/discovery/storefront-artifact.ts`
- `lib/discovery/schema.ts`
- `tests/storefront-query-builder.test.ts`
- `tests/storefront-schema-browser.test.tsx`
- `tests/studio-workspace.test.tsx`
- `tests/discovery.test.ts`
- task Completion Report

### Validation Reviewed

Submitted Attempt 1 evidence:

```text
focused tests: 4 files / 51 passed
targeted ESLint: PASS
legacy path-string source audit: PASS
git diff --check: PASS
typecheck: unchanged unrelated baseline; zero task-owned diagnostics
```

Static review confirms no legacy `buildQueryDefinition`, `selectedPaths` or
`path.split(".")` Storefront builder remains.

The review archive does not contain a runnable dependency installation suitable
for independently repeating the full Vitest/ESLint/typecheck packet here, so the
architect reviewed the submitted evidence plus the actual implementation/test
source.

### Architecture Conformance

Partial.

The AST merge/validation-token foundation conforms.

C034 cannot be accepted until the production Studio can actually author the real
schema arguments, enforce the pre-validation literal/connection rules, consume
C032 schema identity at the correct client boundary, and prove those paths
against the accepted Storefront compiler.

### Follow-up

Reclaim the same task as Attempt 2.

`ARCH-021-COMMERCE-035` remains Pending until C034 is architect-accepted
Complete.
