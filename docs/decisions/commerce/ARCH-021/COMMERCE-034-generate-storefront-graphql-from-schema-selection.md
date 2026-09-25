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
status: in_progress
priority: 30
executor: copilot
claimed_at: 2026-09-25T00:17:18Z
attempt: 4
depends_on:
  - ARCH-021-COMMERCE-033
enables:
  - ARCH-021-COMMERCE-035
created: 2026-09-24
updated: 2026-09-25
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
- [x] Add schema-driven argument-binding state/controls.
- [ ] Add inputSchema-property variable mapping.
- [x] Add bounded literal argument generation.
- [x] Add connection-first handling.
- [x] Merge selections safely into existing query AST.
- [x] Preserve aliases/unrelated existing selections.
- [x] Make pinned schema identity authoritative.
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
- [x] Required schema arguments cannot be bypassed.
- [ ] Input-property variable mappings remain the Tool's persisted argument contract.
- [x] Connection pagination obeys existing bounded compiler policy.
- [x] Existing aliases/unrelated selections survive deterministic merge.
- [x] No dot-path split builder remains.
- [x] Candidate uses the pinned API version/schema hash.
- [ ] `Use in tool` can apply only the exact candidate that passed existing server validation.
- [ ] Real-artifact nested product regression passes.
- [x] No provider/network request occurs during schema authoring/validation.

## Validation

- [ ] `npx vitest run tests/storefront-input-compatibility.test.ts tests/storefront-query-builder.test.ts tests/storefront-argument-bindings.test.tsx tests/storefront-schema-browser.test.tsx tests/studio-workspace.test.tsx tests/discovery.test.ts tests/studio-services.test.ts --reporter=verbose`
- [ ] Existing Storefront compiler/definition tests directly affected by generated queries pass.
- [ ] Targeted ESLint for every Attempt 4 changed source/test file.
- [ ] `npm run typecheck` (unchanged unrelated baseline may be recorded; zero task-owned diagnostics required).
- [ ] Legacy path-string source audit:
  ```text
  rg -n "buildQueryDefinition|path\.split\(\"\\\.\"\)|selectedPaths" components src/studio
  ```
  expected: no legacy Storefront path-string builder matches.
- [ ] Client artifact-boundary audit:
  ```text
  rg -n "storefrontSchemaHash|storefrontArtifact|storefrontSchema" \
    src/studio/discovery components
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
- `lib/discovery/compiler.ts`
- `lib/discovery/storefront-input-compatibility.ts`
- `src/studio/discovery/selection-tree.ts`
- `src/studio/discovery/storefront-argument-bindings.tsx`
- `src/studio/discovery/storefront-query-builder.ts`
- `src/studio/testing/in-memory-studio-services.ts`
- `tests/storefront-argument-bindings.test.tsx`
- `tests/storefront-query-builder.test.ts`
- `tests/storefront-schema-browser.test.tsx`
- `tests/studio-services.test.ts`
- `tests/studio-workspace.test.tsx`
- Attempt 2 implementation commit: `9e180cc2956d50f064825f3e13a2cc72115b7782`
- Attempt 3 implementation commit: `cf3c75b19760329914cfeff41c7056a9e068d18c`

### Work Completed

Attempt 1 established the AST/merge foundation. Attempt 2 added production schema-driven argument-binding state and controls; shared client-safe inputSchema compatibility with the accepted compiler; typed scalar/enum literal generation with explicit unsupported input-object/list rejection; bounded connection `first` handling; authoritative C032 API-version/schema-hash identity; generated-variable collision protection; real compiler-backed validation regressions; and result-path/alias/selection merge safety. Attempt 3 corrected LIST wrapper detection and the first-only/last connection UI policy, removed the task-owned TS2367, and added the required exact-candidate and connected Studio regressions. The legacy dot-path builder remains removed.

### Validation Results

Focused validation passed: `npx vitest run tests/storefront-query-builder.test.ts tests/storefront-argument-bindings.test.tsx tests/storefront-schema-browser.test.tsx tests/studio-workspace.test.tsx tests/discovery.test.ts tests/studio-services.test.ts --reporter=verbose` completed with 6 test files and 70 tests passing. This includes the exact generated nested product candidate through the real compiler, connection `first=1` and `first=20` through the real compiler, LIST/first-only/last UI behavior, fail-closed required/wrong-input workflows, exact schema-identity application, and invalid result-path behavior. The directly affected Storefront definition/compiler tests passed; no provider or network request was used. Targeted ESLint over the five Attempt 3-owned files passed with zero errors/warnings.

The legacy path-string source audit passed: no `buildQueryDefinition`, `path.split(".")`, or `selectedPaths` matches remain in `components` or `src/studio`. The client artifact-boundary audit passed: no runtime Storefront artifact/schema value import remains in the client query-builder/UI surface. `git diff --check` passed.

`npm run typecheck` exits non-zero with the unchanged documented repository baseline, including missing preview modules, Prisma generated-type drift, and existing implicit-any/strictness diagnostics outside the C034-owned files. No diagnostics remain in `components/studio-workspace.tsx`, `src/studio/discovery/storefront-argument-bindings.tsx`, `src/studio/discovery/storefront-query-builder.ts`, or the changed C034 tests; the Attempt 2-owned TS2367 is absent.

Launcher topology evidence: implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-034` and parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-034` both use `task/ARCH-021-COMMERCE-034`. The implementation worktree is clean and `HEAD` equals `origin/task/ARCH-021-COMMERCE-034` at `cf3c75b6a8c5dc003164e9d3aaf1e54b4ecf2c58`. Recursive submodule evidence: `database` at `0a8d3b9feade69690b6c1e33aeda051ea588bd45` (`heads/main`). No ARCH-021-COMMERCE-035 worktree, branch, or implementation was started.

### Deviations

The full repository typecheck remains non-zero only because of unchanged documented baseline diagnostics. Focused tests, targeted ESLint, both source audits, and `git diff --check` passed. No live provider/network request was added or used.

### Assumptions

The accepted Storefront compiler and COMMERCE-032 pinned artifact remain the validation authority. The implementation commit is pushed to `origin/task/ARCH-021-COMMERCE-034`.

### Unresolved Issues

Repository-wide typecheck remains non-zero on unrelated baseline diagnostics; zero task-owned diagnostics are present.

### Architectural Concerns

None identified within the bounded task scope.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 3 successfully resolves the two production-source findings from Attempt 2:

- LIST wrappers are now detected from the original `StorefrontTypeRef`, so the task-owned `TS2367` is gone and LIST literals no longer receive a scalar editor;
- every real argument named `first`, including first-only Shopify fields such as `productTags(first: Int!)`, now receives the literal-only `1..20` UI policy;
- normal UI authoring for `last` is removed while builder-side stale/manual rejection remains;
- the Attempt 3 focused packet reports 70 passing tests and zero C034-owned typecheck diagnostics.

Those corrections are accepted in substance.

There is one remaining source correctness blocker and two regression-evidence defects.

#### Finding 1 — the shared input compatibility helper accepts strings for Boolean/Int/Float

The C034-owned shared helper currently contains:

```ts
if (expected.kind === 'ENUM' || expected.kind === 'SCALAR')
  return propertySchema.type === 'string'
    || (expected.name === 'Boolean' && propertySchema.type === 'boolean')
    || (expected.name === 'Int' && (...))
    || (expected.name === 'Float' && (...));
```

The first condition:

```ts
propertySchema.type === 'string'
```

is unconditional for every `SCALAR`.

Therefore these invalid mappings currently return `true`:

```text
Tool input type string -> GraphQL Boolean
Tool input type string -> GraphQL Int
Tool input type string -> GraphQL Float
```

This is a real C034 correctness defect because the builder and the accepted compiler now share this helper. A bad mapping can therefore pass both client candidate construction and server mapped-argument validation.

The real pinned C032 graph contains concrete arguments affected by this, for example:

```text
QueryRoot.products.reverse: Boolean
QueryRoot.predictiveSearch.limit: Int
```

This violates R3's requirement that `INPUT_PROPERTY` compatibility match the actual GraphQL argument type.

Attempt 4 must preserve the intended compatibility matrix explicitly.

Required scalar behavior:

```text
ENUM                  -> string
Boolean               -> boolean
Int                   -> integer OR number
Float                 -> number OR integer
String                -> string
ID                    -> string
URL                   -> string
HTML                  -> string
Date                  -> string
DateTime              -> string
other/custom SCALAR   -> string
```

Do not restore a separate compiler-only compatibility function. The same
`storefrontInputSchemaCompatible()` helper remains authoritative for builder and
compiler.

Do not weaken list/input-object compatibility while fixing scalar handling.

Create:

```text
tests/storefront-input-compatibility.test.ts
```

and prove at minimum:

```text
string -> String       true
string -> Boolean      false
boolean -> Boolean     true
string -> Int          false
integer -> Int         true
number -> Int          true   # preserve accepted previous compiler semantics
string -> Float        false
number -> Float        true
string -> enum         true
array(items:string) -> [String] true
```

Also retain/add one real-schema builder regression using:

```text
products.reverse: Boolean
```

with:

```text
inputSchema.reverse.type = string
products.first = literal 1
products.reverse = INPUT_PROPERTY(reverse)
```

and prove candidate construction fails visibly with:

```text
Input property reverse is incompatible with GraphQL argument Boolean.
```

That proves the shared helper is actually used by the C034 builder rather than only unit-tested in isolation.

#### Finding 2 — the "exact generated nested product candidate" regression still starts from an already-authored `product`

Attempt 3 added:

```text
passes the exact generated nested product candidate through the real compiler
```

but it builds from:

```ts
fixtureToolDefinition('catalog_lookup')
```

whose existing document is already:

```graphql
query ProductDetails($handle: String!) {
  product(handle: $handle) {
    title
    availableForSale
  }
}
```

Therefore the builder finds the existing `product` field and, correctly under R6,
preserves its existing arguments. The supplied binding:

```text
product.handle -> INPUT_PROPERTY(handle)
```

is not what creates the root argument in this test.

The resulting compiler success proves nested merge into an existing product, not
the R11 requirement that C034 generate the mapped `product.handle` argument from
the selected schema/binding state.

Attempt 4 must make this exact regression start from a document with **no existing
`product` root**, for example:

```graphql
query ProductDetails {
  shop {
    name
  }
}
```

with an otherwise valid Tool definition and `resultPath: "shop"`.

Build:

```text
QueryRoot.product
  -> Product.priceRange
    -> ProductPriceRange.minVariantPrice
      -> MoneyV2.amount
```

with:

```text
product.handle -> INPUT_PROPERTY(handle)
```

Then prove the exact generated candidate contains:

```text
product(handle: $input_handle)
execution.variables.input_handle -> input "handle"
```

and pass that **same unmodified generated candidate** through
`InMemoryStudioServices.validateToolDefinition()` / the real compiler.

The test name must not call `product.handle` required; C032 correctly defines it
as optional.

#### Finding 3 — the connected schema-identity test still compares only the query after application

Attempt 2's correction contract explicitly required:

```text
Use in tool applies the same complete candidate definition that was validated
```

and explicitly said:

```text
Do not compare only the query string; compare the complete candidate definition
or a stable structural clone/hash of it.
```

Attempt 3 currently captures the complete definition sent to
`validateToolDefinition`, but after `Use in tool` it asserts only:

```ts
appliedQuery.value === validatedDefinition.execution.document
```

The production source itself currently uses the same `proposed` object for both
validation and `composer.setTool`, which is correct, but the required connected
regression is still weaker than the correction contract.

Complete the regression without adding a production test seam.

A conformant test-only harness can render a small probe inside the existing
`StudioComposerProvider` using the existing exported `useStudioComposer()` hook,
for example by serializing:

```text
composer.tool?.definition
```

to a test-only `<output data-testid="...">`.

Required proof:

1. capture a structural clone of the exact definition passed to
   `validateToolDefinition`;
2. validation succeeds;
3. click `Use in tool`;
4. read the definition from the real composer context after application;
5. assert deep structural equality with the captured validated definition.

Do not modify `StudioWorkspace` to expose a test callback/port/prop.

### Attempt 4 deterministic correction

Reclaim the same task as Attempt 4.

This is a narrow correctness/evidence pass. Preserve all accepted Attempt 1-3
behavior:

```text
AST merge
C033 selection tree
argument-binding editor
typed literal generation
LIST/input-object literal rejection
first-only/last UI policy
connection first 1..20
C032 schema identity
variable collision protection
validation token/hash behavior
real compiler validation
resultPath preservation
```

#### Source changes

Expected production source change is primarily:

```text
lib/discovery/storefront-input-compatibility.ts
```

Change other production files only if the new regressions expose a real defect.

#### Required tests

Add:

```text
tests/storefront-input-compatibility.test.ts
```

with the compatibility matrix above.

Update:

```text
tests/storefront-query-builder.test.ts
```

to:

- prove real `products.reverse: Boolean` rejects a string Tool input;
- make the nested product compiler regression genuinely generate
  `product(handle: $input_handle)` from a product-free base document;
- pass the exact generated candidate to the real compiler without substituting a
  hand-authored query.

Update:

```text
tests/studio-workspace.test.tsx
```

so the schema-identity flow compares the entire composer-applied definition with
the exact complete definition previously sent to validation.

Retain the already-passing Attempt 3 regressions:

```text
LIST literal UI
first-only literal-only UI
last authoring blocked
first=1 and first=20 through real compiler
missing required argument does not call validation
wrong input type does not call validation
invalid resultPath keeps Use in tool disabled
```

#### Validation

Run the task Validation section exactly, including the new compatibility test.

Typecheck acceptance remains:

```text
unchanged documented unrelated repository baseline is permitted
zero C034-owned diagnostics are required
```

Run both existing source audits and `git diff --check`.

#### Completion Report

Update the report to distinguish:

```text
Attempt 1:
  AST/merge foundation

Attempt 2:
  production argument binding + schema identity + compiler integration

Attempt 3:
  LIST/first-only/last UI parity + TS2367 cleanup + connected regressions

Attempt 4:
  exact scalar input-compatibility parity
  genuinely generated nested product compiler proof
  full-definition validated/applied identity proof
```

Record:

```text
Attempt 4 implementation/test commit
final parent report commit
focused test files/count
ESLint
typecheck baseline and zero task-owned diagnostics
both source audits
git diff --check
branch/worktree synchronization
database submodule synchronization
```

Return:

```yaml
status: review
executor: null
claimed_at: null
attempt: 4
```

and STOP.

Do not start `ARCH-021-COMMERCE-035`.

### Reviewed Files

- `components/studio-workspace.tsx`
- `lib/discovery/compiler.ts`
- `lib/discovery/storefront-input-compatibility.ts`
- `src/studio/discovery/storefront-argument-bindings.tsx`
- `src/studio/discovery/storefront-query-builder.ts`
- `src/studio/testing/in-memory-studio-services.ts`
- `tests/storefront-argument-bindings.test.tsx`
- `tests/storefront-query-builder.test.ts`
- `tests/storefront-schema-browser.test.tsx`
- `tests/studio-workspace.test.tsx`
- `tests/discovery.test.ts`
- `tests/studio-services.test.ts`
- task Completion Report

### Validation Reviewed

Submitted Attempt 3 evidence:

```text
focused tests: 6 files / 70 passed
targeted ESLint: PASS
legacy path-string audit: PASS
client artifact-boundary audit: PASS
git diff --check: PASS
typecheck: unchanged unrelated baseline only
           zero C034-owned diagnostics
```

Architect static review confirms the previous `TS2367`, LIST-wrapper bug and
first-only pagination UI bug are resolved.

Architect static review also confirms the remaining compatibility defect described
above directly from `storefrontInputSchemaCompatible()`.

The supplied archive does not contain installed dependencies, so the architect
did not independently rerun Vitest/ESLint/typecheck.

### Architecture Conformance

Partial.

The overall C034 architecture now conforms, but acceptance is blocked by one
C034-owned shared compatibility defect and the two exact regression-evidence
requirements above.

### Follow-up

Reclaim the same task as Attempt 4.

`ARCH-021-COMMERCE-035` remains Pending until C034 is architect-accepted Complete.
