---
id: ARCH-021-COMMERCE-063
architecture_id: ARCH-021
title: Compile Tool result contracts and validate result templates
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 72
executor: copilot
claimed_at: 2026-09-27T15:05:20Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-043
enables:
  - ARCH-021-COMMERCE-066
  - ARCH-021-COMMERCE-067
created: 2026-09-27
updated: 2026-09-27
---

# Compile Tool result contracts and validate result templates

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Introduce one source-neutral, non-persisted `ToolResultContract` compiler over the canonical Tool output schema and one non-mutating Result Template validation boundary so Shopify and Custom Tool authoring can derive the same exact template fields/tokens from `data.values` without duplicating schema-walking rules in React or publication code.

## Context

The current system already has the important primitives:

```text
CommerceResultSchema
externalOutputSchema(resultSchema)
Admin compiler outputSchema
responseTemplateCompatibilityIssues(...)
renderDefinitionResult(...)
```

But there is no first-class authoring contract that enumerates the fields a Result Template can reference. `responseTemplate` validation is currently folded into Agent Contract validation and publication.

This task creates that derived contract and validation boundary only. It does not create the UI.

## Scope

Expected implementation areas include:

```text
src/commerce/tool-definition/
src/commerce/tool-authoring/                  # new result-template boundary
src/commerce/execution/renderer.ts             # reuse semantics, minimal extraction only
src/studio/tools/*server-actions*.ts           # non-mutating validation action if required

tests/arch021-commerce-tool-contract.test.ts
focused ToolResultContract/result-template tests
```

## Out of Scope

- React Result Template tab; COMMERCE-066 owns it.
- Moving fields out of Agent Contract UI; COMMERCE-068 owns integration.
- Shopify result-schema derivation; COMMERCE-062 owns it.
- External HTTP Response processing/inference changes.
- New template syntax, conditionals, loops or arbitrary JavaScript.
- Persisting a separate tag/binding catalogue.
- Provider I/O or Tool persistence.

## Requirements

### R1 — derived contract, never a second source of truth

Add a pure compiler conceptually equivalent to:

```text
compileToolResultContract(outputSchema)
```

The result is derived from the canonical Tool output schema and is never persisted independently.

Changing the underlying output schema must deterministically change the derived bindings.

### R2 — canonical namespace is `result.values`

For Shopify Admin and External HTTP Tool results, generated scalar tokens must target the normalized result data namespace, for example:

```text
{{result.values.title}}
{{result.values.price.amount}}
```

Do not generate provider/raw-response paths.

### R3 — enumerate scalar bindings with metadata

For every reachable scalar property, derive bounded metadata sufficient for UI and validation, including:

```text
path
token
scalar type
required/optional status
human-readable path segments
```

Required/optional status must follow the canonical result schema's `required` arrays across the full ancestor path.

Optional scalars may remain valid under the existing renderer's `unavailable` fallback semantics; the contract must make their optional status explicit so UI can communicate it.

### R4 — enumerate supported collection bindings

For arrays of objects that can be used by existing `responseTemplate.kind = "items"`, expose:

```text
itemsPath
item scalar bindings
item field required/optional metadata
```

Do not claim support for a collection form the current renderer cannot express. Primitive scalar arrays, arrays-of-arrays or other unsupported item-template shapes must be marked non-templateable rather than given invalid `{{item.*}}` tokens.

### R5 — one template compatibility implementation

Refactor/reuse `responseTemplateCompatibilityIssues` so authoring validation and publication use the same path/type interpretation.

At minimum validate:

```text
text/items template canonical shape
token syntax
result/item prefix
path existence
scalar-only token targets
itemsPath resolves to an allowed collection
item paths resolve within the selected item schema
```

Do not maintain a UI-only validator with different rules.

### R6 — non-mutating Result Template validation boundary

Expose one named authoring validator for:

```text
responseTemplate
current output/result contract
```

It must return deterministic bounded issues with Result-Template-local paths and perform no Request execution, provider call, Tool write or publication.

### R7 — preserve runtime rendering semantics

The existing renderer remains deterministic and bounded. This task may extract shared helpers, but it must not silently change the meaning of already-valid text/items templates outside the explicitly accepted compatibility rules.

## Work Items

- [ ] Add the pure `ToolResultContract` compiler.
- [ ] Derive scalar binding/token metadata from canonical output schemas.
- [ ] Derive supported item-collection binding metadata.
- [ ] Mark unsupported collection/template shapes truthfully.
- [ ] Consolidate response-template compatibility rules into one reusable boundary.
- [ ] Add non-mutating Result Template authoring validation.
- [ ] Add nested object, optional field, items-template and invalid-path tests.

## Interfaces / Contracts

Consumes canonical Commerce output schemas. For current authoring paths these are equivalent to:

```text
{ values: execution.resultSchema }
```

Produces a non-persisted Commerce-internal `ToolResultContract`/binding catalogue and bounded validation result.

No Shared package contract or database state is added.

## Dependencies

- `ARCH-021-COMMERCE-043`

## Enables

- `ARCH-021-COMMERCE-066`
- `ARCH-021-COMMERCE-067`

## Acceptance Criteria

- [ ] The same canonical output schema always yields the same binding catalogue.
- [ ] Nested scalar paths generate exact `{{result.values.*}}` tokens.
- [ ] Required/optional metadata is correct through nested objects.
- [ ] Arrays of objects expose supported `itemsPath` + `item` bindings.
- [ ] Unsupported collection shapes do not generate invalid item tokens.
- [ ] Unknown/object/array scalar-token paths are rejected deterministically.
- [ ] Authoring validation and publication reuse the same compatibility logic.
- [ ] No tag/binding catalogue is persisted.
- [ ] No provider I/O or durable writes occur.

## Validation

- [ ] focused ToolResultContract compiler tests
- [ ] focused Result Template validation tests
- [ ] publication compatibility tests
- [ ] renderer regression tests
- [ ] targeted lint
- [ ] changed-file TypeScript diagnostics
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin COMMERCE-066 or COMMERCE-067.

## Implementation Notes

Keep the compiler independent of Shopify/External provider types. Provider-specific logic should already have produced the canonical output schema before this boundary.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

None.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending review.

### Follow-up

None.
