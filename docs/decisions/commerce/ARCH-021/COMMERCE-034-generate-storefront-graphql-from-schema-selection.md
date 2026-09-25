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
status: complete
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

- [x] `npx vitest run tests/storefront-input-compatibility.test.ts tests/storefront-query-builder.test.ts tests/storefront-argument-bindings.test.tsx tests/storefront-schema-browser.test.tsx tests/studio-workspace.test.tsx tests/discovery.test.ts tests/studio-services.test.ts --reporter=verbose`
- [x] Existing Storefront compiler/definition tests directly affected by generated queries pass.
- [x] Targeted ESLint for every Attempt 5 changed source/test file.
- [x] `npm run typecheck` (unchanged unrelated baseline may be recorded; zero task-owned diagnostics required).
- [x] Legacy path-string source audit:
  ```text
  rg -n "buildQueryDefinition|path\.split\(\"\\\.\"\)|selectedPaths" components src/studio
  ```
  expected: no legacy Storefront path-string builder matches.
- [x] Client artifact-boundary audit:
  ```text
  rg -n "storefrontSchemaHash|storefrontArtifact|storefrontSchema" \
    src/studio/discovery components
  ```
  expected: no runtime Storefront artifact/schema value import in client query-builder/UI code.
- [x] `git diff --check`

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

Accepted

### Review Notes

Attempt 5 resolves the final two bounded correctness findings from Attempt 4.

Architect review confirms the production query builder now fails closed when the deterministic generated variable name already exists in the authored GraphQL operation but the corresponding persisted Tool input mapping is missing:

```ts
if (
  existing &&
  (
    !existingMapping ||
    !('input' in existingMapping) ||
    existingMapping.input !== generated.property
  )
) {
  throw new Error(
    `Generated variable ${name} conflicts with the existing input mapping.`,
  );
}
```

This preserves the required collision invariant:

```text
existing variable definition
  -> same GraphQL type required
  -> existing INPUT_PROPERTY mapping required
  -> same requested input property required
  -> otherwise reject
```

The accepted reuse case is also covered: an existing variable with the same GraphQL type and the exact existing input mapping is reused without adding a duplicate variable definition or mapping.

The Int literal editor now preserves the authored numeric value using:

```ts
Number(value)
```

rather than `Number.parseInt(...)`.

Therefore:

```text
"1.5" -> 1.5
```

reaches the typed AST builder and is rejected by the existing:

```text
Literal for Int must be a finite integer.
```

rule rather than being silently changed to `1`.

A valid integer such as:

```text
"5" -> 5
```

remains valid.

### Final C034 architecture accepted

Across Attempts 1-5, the final Storefront query-authoring path now provides:

```text
real C032 schema graph
        +
C033 nested selection tree
        +
schema-driven argument bindings
        +
C032 apiVersion/schemaHash
        |
        v
GraphQL AST generation/merge
        |
        v
exact ToolDefinition candidate
        |
        v
named validateToolDefinition Server Action
        |
        v
accepted Storefront compiler
        |
        v
Use in tool only for the exact validated candidate
```

The final accepted behavior includes:

- no legacy dot-path query builder;
- schema-driven `INPUT_PROPERTY` and `LITERAL` argument authoring;
- shared client/server input-schema compatibility;
- typed scalar/enum literal generation;
- LIST/input-object literal rejection;
- connection `first` literal bound from 1 through 20;
- no authored `last`;
- alias/unrelated selection preservation;
- duplicate/ambiguous existing field rejection;
- deterministic variable naming and ordering;
- fail-closed variable type/mapping collision handling;
- C032 schema identity applied to both API version and schema hash;
- visible schema-identity rebuild/revalidation;
- real compiler as final validation authority;
- resultPath preservation/failure through the existing validation path;
- complete validated/applied Tool definition identity;
- no normal provider/network request during schema authoring.

### Attempt 5 evidence

Architect inspected the final production source and tests and confirmed the required regressions are present:

```text
existing generated-name variable + missing mapping -> rejected
existing generated-name variable + identical mapping/type -> reused
no duplicate generated variable/mapping introduced
predictiveSearch.limit literal 1.5 retained as 1.5 and rejected by builder
predictiveSearch.limit literal 5 retained and accepted
```

Submitted validation:

```text
focused tests: 7 files / 82 passed
targeted ESLint: PASS
legacy path-string audit: PASS
client artifact-boundary audit: PASS
git diff --check: PASS
typecheck: unchanged unrelated repository baseline only
           zero C034-owned diagnostics
```

The review archive does not contain `node_modules`, so the architect did not independently rerun Vitest/ESLint/typecheck. The final implementation and focused regression source were inspected directly.

Implementation reviewed:

```text
2a49b270
```

Final parent report supplied by the handoff:

```text
869af5d3
```

As with prior task reports, the final parent-report SHA is supplied by the handoff because the report file cannot reliably contain the SHA of the commit that subsequently publishes that same final report.

### Reviewed Files

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
- `tests/studio-workspace.test.tsx`
- `tests/discovery.test.ts`
- `tests/studio-services.test.ts`
- task Completion Report

### Validation Reviewed

The task Validation checklist is reconciled as satisfied under the explicit allowed typecheck rule:

```text
unchanged unrelated baseline diagnostics are permitted
zero task-owned diagnostics are required
```

All submitted Attempt 5 focused validation satisfies that contract.

### Architecture Conformance

Conforms.

C034 now deterministically builds and merges Storefront GraphQL from the real schema-backed selection/binding state and validates the exact candidate against the accepted compiler before application.

### Follow-up

`ARCH-021-COMMERCE-034` is Complete.

`ARCH-021-COMMERCE-035` becomes Ready.

The previously requested C035 UI-component boundary is materialized before promotion:

```text
StudioWorkspace
  -> ShopifyDocumentationExplorer
      -> ShopifyDocumentationArticle
```

`ARCH-021-SYSTEM-TEST-001` remains Pending until C035 is architect-accepted Complete.

Do not start SYSTEM-TEST-001.
