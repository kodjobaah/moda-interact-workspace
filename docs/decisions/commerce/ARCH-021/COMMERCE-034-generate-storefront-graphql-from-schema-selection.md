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
src/studio/discovery/storefront-query-builder.ts   # new pure AST generator/merge logic
src/studio/discovery/storefront-schema-browser.tsx # argument-binding controls + generated preview
src/studio/discovery/selection-tree.ts
components/studio-workspace.tsx                    # remove old buildQueryDefinition/addPath path-string builder
lib/discovery/compiler.ts                          # expose/reuse bounded helpers only if needed
tests/storefront-query-builder.test.ts             # new
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

with `product`'s required argument bound to a top-level Tool input property.

The resulting candidate must contain a valid named query and pass the existing Storefront compiler.

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

- [x] Focused Vitest suite — 4 files, 51 tests passed, including the in-memory Studio validation-boundary regression.
- [x] Existing Storefront compiler/definition coverage — affected compiler validation tests in `tests/discovery.test.ts` pass.
- [x] Targeted ESLint for every changed source/test file — passed with zero errors and warnings after removing the stale `parse` import.
- [ ] `npm run typecheck` — blocked by unchanged unrelated baseline diagnostics in Prisma-generated/database integration and other existing strictness failures; zero diagnostics remain in task-owned files after repair.
- [x] Source audit:
  ```text
  rg -n "buildQueryDefinition|path\.split\(\"\\.\"\)|selectedPaths" components src/studio
  ```
  no legacy Storefront path-string builder matches.
- [x] `git diff --check` — passed.

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
