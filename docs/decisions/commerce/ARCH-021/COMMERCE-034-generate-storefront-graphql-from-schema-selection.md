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
status: review
priority: 30
executor: null
claimed_at: null
attempt: 5
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
- [x] Add inputSchema-property variable mapping.
- [x] Add bounded literal argument generation.
- [x] Add connection-first handling.
- [x] Merge selections safely into existing query AST.
- [x] Preserve aliases/unrelated existing selections.
- [x] Make pinned schema identity authoritative.
- [x] Wire exact candidate through existing `validateToolDefinition`.
- [x] Remove old dot-path query-generation code.
- [x] Add real-artifact integrated regressions.

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
- [x] Input-property variable mappings remain the Tool's persisted argument contract.
- [x] Connection pagination obeys existing bounded compiler policy.
- [x] Existing aliases/unrelated selections survive deterministic merge.
- [x] No dot-path split builder remains.
- [x] Candidate uses the pinned API version/schema hash.
- [x] `Use in tool` can apply only the exact candidate that passed existing server validation.
- [x] Real-artifact nested product regression passes.
- [x] No provider/network request occurs during schema authoring/validation.

## Validation

- [ ] `npx vitest run tests/storefront-input-compatibility.test.ts tests/storefront-query-builder.test.ts tests/storefront-argument-bindings.test.tsx tests/storefront-schema-browser.test.tsx tests/studio-workspace.test.tsx tests/discovery.test.ts tests/studio-services.test.ts --reporter=verbose`
- [ ] Existing Storefront compiler/definition tests directly affected by generated queries pass.
- [ ] Targeted ESLint for every Attempt 5 changed source/test file.
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
- `tests/storefront-input-compatibility.test.ts`
- `tests/storefront-argument-bindings.test.tsx`
- `tests/storefront-query-builder.test.ts`
- `tests/storefront-schema-browser.test.tsx`
- `tests/studio-services.test.ts`
- `tests/studio-workspace.test.tsx`
- Attempt 2 implementation commit: `9e180cc2956d50f064825f3e13a2cc72115b7782`
- Attempt 3 implementation commit: `cf3c75b19760329914cfeff41c7056a9e068d18c`
- Attempt 4 implementation commit: `caa900a`
- Attempt 5 implementation/test commit: `2a49b270cf12d74b88c807c5156029786b09c65f`

### Work Completed

Attempt 1 established the AST/merge foundation.

Attempt 2 added production schema-driven argument-binding state and controls; shared client-safe inputSchema compatibility with the accepted compiler; typed scalar/enum literal generation with explicit unsupported input-object/list rejection; bounded connection `first` handling; authoritative C032 API-version/schema-hash identity; generated-variable collision protection; real compiler-backed validation regressions; and result-path/alias/selection merge safety.

Attempt 3 corrected LIST wrapper detection and the first-only/last connection UI policy, removed the task-owned TS2367, and added the required connected Studio regressions. The legacy dot-path builder remained removed.

Attempt 4 corrected scalar compatibility parity so String is no longer accepted for GraphQL Boolean, Int or Float; retained integer/number compatibility for Int and integer/number compatibility for Float; added the required compatibility matrix; added a real `products.reverse: Boolean` builder regression; changed the nested product compiler proof to start from a product-free document and verify generated `product(handle: $input_handle)` plus its persisted mapping; and changed the schema-identity connected regression to deep-compare the complete validated definition with the definition applied in the real composer context.

Attempt 5 now fails closed when a deterministic generated variable already exists without the exact persisted input mapping, while retaining exact type-and-mapping reuse without duplicate definitions or mappings. The argument editor preserves non-truncating GraphQL Int values, and real `predictiveSearch.limit` regressions prove `1.5` reaches the typed builder and is rejected while `5` remains valid.

### Validation Results

Focused validation passed: `npx vitest run tests/storefront-input-compatibility.test.ts tests/storefront-query-builder.test.ts tests/storefront-argument-bindings.test.tsx tests/storefront-schema-browser.test.tsx tests/studio-workspace.test.tsx tests/discovery.test.ts tests/studio-services.test.ts --reporter=verbose` completed with 7 test files and 82 tests passing. This includes the Attempt 5 missing-mapping rejection/document-preservation and exact reuse regressions, non-truncating real `predictiveSearch.limit` Int literal regressions (`1.5` rejected and `5` accepted), scalar compatibility matrix, real `products.reverse: Boolean` rejection for a string input property, generated nested product mapping through the real compiler from a product-free base document, connection `first=1` and `first=20`, LIST/first-only/last UI behavior, fail-closed required/wrong-input workflows, exact complete-definition schema-identity application, and invalid result-path behavior. No provider or network request was used.

Targeted ESLint over every Attempt 5 changed source/test file passed with zero errors/warnings. `npm run typecheck` exits non-zero with the unchanged documented repository baseline, including missing preview modules, Prisma generated-type drift, and existing implicit-any/strictness diagnostics outside the C034-owned files. The full output contains no diagnostics for the changed C034 helper, builder, workspace, or tests.

The legacy path-string source audit passed: no `buildQueryDefinition`, `path.split(".")`, or `selectedPaths` matches remain in `components` or `src/studio`. The client artifact-boundary audit passed: no runtime Storefront artifact/schema value import remains in the client query-builder/UI surface. `git diff --check` passed.

`npm run typecheck` exits non-zero with the unchanged documented repository baseline, including missing preview modules, Prisma generated-type drift, and existing implicit-any/strictness diagnostics outside the C034-owned files. No diagnostics remain in `components/studio-workspace.tsx`, `src/studio/discovery/storefront-argument-bindings.tsx`, `src/studio/discovery/storefront-query-builder.ts`, or the changed C034 tests; the Attempt 2-owned TS2367 is absent.

Launcher topology evidence: implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-034` and parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-034` both use `task/ARCH-021-COMMERCE-034`. Attempt 5 implementation commit `2a49b270cf12d74b88c807c5156029786b09c65f` is pushed to `origin/task/ARCH-021-COMMERCE-034`; the implementation worktree is clean. The database submodule remains pinned at `0a8d3b9feade69690b6c1e33aeda051ea588bd45` (`heads/main`). No ARCH-021-COMMERCE-035 worktree, branch, or implementation was started.

### Deviations

The full repository typecheck remains non-zero only because of unchanged documented baseline diagnostics; zero C034-owned diagnostics are present. Focused tests (7 files / 82 tests), targeted ESLint, both source audits, and `git diff --check` passed. No live provider/network request was added or used.

### Assumptions

The accepted Storefront compiler and COMMERCE-032 pinned artifact remain the validation authority. Attempt 5 implementation commit `2a49b270cf12d74b88c807c5156029786b09c65f` is pushed to `origin/task/ARCH-021-COMMERCE-034`.

### Unresolved Issues

Repository-wide typecheck remains non-zero on unrelated baseline diagnostics; zero task-owned diagnostics are present.

### Architectural Concerns

None identified within the bounded task scope.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 4 successfully resolves the three findings from Attempt 3.

Architect review confirms:

- `storefrontInputSchemaCompatible()` now distinguishes GraphQL scalar names correctly:
  - String/custom scalar -> string;
  - Boolean -> boolean;
  - Int -> integer/number;
  - Float -> integer/number;
  - enum -> string;
- the dedicated compatibility matrix covers the required scalar/list cases;
- the real `products.reverse: Boolean` builder regression rejects a string Tool input;
- the nested `product -> priceRange -> minVariantPrice -> amount` compiler regression now starts from a product-free document, generates `product(handle: $input_handle)`, persists `input_handle -> handle`, and sends that exact generated candidate to the real compiler;
- the connected schema-identity regression now reads the real composer context after `Use in tool` and deep-compares the complete applied Tool definition with the complete definition previously sent to `validateToolDefinition`;
- the Attempt 4 focused packet reports 7 files / 80 tests passing with zero C034-owned typecheck diagnostics.

Those corrections are accepted.

There are two remaining bounded C034 correctness issues.

#### Finding 1 — an existing generated-name GraphQL variable with no mapping is silently assigned a new input mapping

The Attempt 1 correction contract explicitly required that, before reusing a generated variable name already present in the current operation, **both** of these must already agree:

```text
existing GraphQL variable type == generated expected type
existing execution.variables mapping == requested INPUT_PROPERTY
```

and:

```text
if either differs, fail visibly
```

The current source checks the existing variable type and checks an existing mapping only when one is already present:

```ts
const existing = existingDefinitions.get(name);
const existingMapping = definition.execution.variables[name];

if (existing && print(existing.type) !== print(generated.type)) {
  throw ...
}

if (existingMapping && (...mapping differs...)) {
  throw ...
}

if (existingMapping && !existing) {
  throw ...
}
```

If:

```text
$input_handle already exists in the authored GraphQL operation
execution.variables.input_handle is absent
```

the code does not fail.

Later it executes:

```ts
if (!nextMappings[name]) {
  nextMappings[name] = { input: value.property };
}
```

so the existing variable silently acquires a new Tool input mapping.

That can change the semantics of every existing use of `$input_handle` in the preserved query. It violates R6 ("do not silently rewrite an existing argument binding") and the explicit generated-variable collision contract from Attempt 1.

Attempt 5 must fail closed when an existing variable definition occupies the deterministic generated name but the matching execution mapping is missing.

A conformant structure is:

```text
if existing GraphQL variable exists:
    require same GraphQL type
    require existing execution mapping exists
    require mapping kind is INPUT_PROPERTY
    require mapping input == requested property
    otherwise throw bounded conflict

if existing execution mapping exists but GraphQL variable does not:
    throw bounded conflict

only when neither exists:
    create both definition and mapping
```

Use the existing bounded conflict wording where practical. Do not silently invent a mapping for a pre-existing variable.

Required regression:

```graphql
query ProductDetails($input_handle: String) {
  shop {
    name
  }
}
```

with:

```text
execution.variables = {}
product.handle -> INPUT_PROPERTY(handle)
```

must fail visibly and leave the original definition unchanged.

Also retain/prove the allowed reuse case:

```text
existing $input_handle: String
existing execution.variables.input_handle -> input "handle"
new product.handle expects String
```

must reuse the existing definition/mapping without duplication.

#### Finding 2 — the Int literal editor truncates invalid decimal/exponent input before the AST builder can reject it

The production argument editor currently parses Int text with:

```ts
Number.parseInt(value, 10)
```

Therefore user-entered values such as:

```text
1.5
1e2
```

can be converted before C034's typed literal validator sees the original number:

```text
"1.5" -> 1
"1e2" -> 1
```

The AST builder then sees a valid integer and cannot report that the authored literal was invalid.

This violates R3's requirement that scalar literals be type checked against the actual GraphQL argument type rather than heuristically coerced.

Attempt 5 must preserve the numeric value faithfully and let the existing `valueNode()` checks decide validity.

For numeric scalar editor input:

```text
empty string -> non-finite/invalid sentinel that builder rejects when candidate is built
otherwise -> Number(value)
```

or an equivalent non-truncating implementation is acceptable.

Do not use `parseInt()` for GraphQL Int authoring.

Required regressions:

1. Use the real C032 argument:

   ```text
   predictiveSearch.limit: Int
   ```

   or another real non-connection Int argument.

2. In the production argument editor test, enter:

   ```text
   1.5
   ```

   and prove the emitted binding retains `1.5` rather than becoming `1`.

3. Pass that binding through `buildStorefrontQueryDefinition()` and prove candidate generation fails with the existing typed error:

   ```text
   Literal for Int must be a finite integer.
   ```

4. Retain a valid integer literal regression proving `5` remains `5`.

Do not change connection `first` semantics; the existing literal `1..20` policy remains accepted.

### Attempt 5 deterministic correction

Reclaim the same task as Attempt 5.

This is a narrow final correctness pass. Preserve all accepted Attempt 1-4 behavior:

```text
AST merge
C033 selection tree
argument-binding editor
shared input compatibility
typed enum/scalar literals
LIST/input-object literal rejection
first-only/last authoring policy
connection first 1..20
C032 schema identity
generated-variable type/mapping collision protection
validation token/hash behavior
real compiler validation
resultPath preservation
full-definition validated/applied identity
```

Expected production source changes are limited to:

```text
src/studio/discovery/storefront-query-builder.ts
src/studio/discovery/storefront-argument-bindings.tsx
```

Change another production file only if the required regressions expose a directly related defect.

#### Required tests

Update `tests/storefront-query-builder.test.ts` to prove:

```text
existing generated-name variable + missing execution mapping -> rejected
existing generated-name variable + identical existing mapping/type -> reused
no duplicate variable definition/mapping is introduced
real Int argument with literal 1.5 -> typed builder rejection
real Int argument with literal 5 -> accepted as Int
```

Update `tests/storefront-argument-bindings.test.tsx` to prove the real Int editor does not truncate `1.5` to `1`.

Retain all Attempt 4 regressions, especially:

```text
scalar compatibility matrix
products.reverse Boolean/string rejection
exact generated nested product through real compiler
first=1 / first=20 through real compiler
LIST literal UI
first-only/last UI behavior
missing required argument blocks server validation
wrong input type blocks server validation
full-definition schema-identity validate/apply equality
invalid resultPath keeps Use in tool disabled
```

#### Validation

Run the task Validation section exactly.

Typecheck acceptance remains:

```text
unchanged documented unrelated baseline is permitted
zero C034-owned diagnostics are required
```

Run both source audits and `git diff --check`.

#### Completion Report

Update the report to distinguish:

```text
Attempt 1:
  AST/merge foundation

Attempt 2:
  argument binding + schema identity + compiler integration

Attempt 3:
  LIST/first-only/last parity + TS2367 cleanup + connected regressions

Attempt 4:
  scalar compatibility parity
  genuinely generated nested candidate
  full-definition validated/applied identity

Attempt 5:
  fail-closed existing-variable/missing-mapping collision
  non-truncating GraphQL Int literal authoring
```

Record:

```text
Attempt 5 implementation/test commit
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
attempt: 5
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
- `tests/storefront-input-compatibility.test.ts`
- `tests/storefront-argument-bindings.test.tsx`
- `tests/storefront-query-builder.test.ts`
- `tests/storefront-schema-browser.test.tsx`
- `tests/studio-workspace.test.tsx`
- `tests/discovery.test.ts`
- `tests/studio-services.test.ts`
- task Completion Report

### Validation Reviewed

Submitted Attempt 4 evidence:

```text
focused tests: 7 files / 80 passed
targeted ESLint: PASS
legacy path-string audit: PASS
client artifact-boundary audit: PASS
git diff --check: PASS
typecheck: unchanged unrelated baseline only
           zero C034-owned diagnostics
```

Architect static review confirms the Attempt 3 scalar compatibility defect is fixed,
the generated nested product regression now genuinely uses the supplied binding,
and the complete validated/applied definition identity assertion is present.

The remaining variable/mapping collision and Int parsing findings are directly
visible in the final production source described above.

### Architecture Conformance

Partial.

The complete C034 architecture now conforms except for the two bounded correctness
cases in Attempt 5.

### Follow-up

Reclaim the same task as Attempt 5.

`ARCH-021-COMMERCE-035` remains Pending until C034 is architect-accepted Complete.
