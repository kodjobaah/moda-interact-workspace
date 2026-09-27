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
status: complete
priority: 72
executor: null
claimed_at: null
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

- [x] Add the pure `ToolResultContract` compiler.
- [x] Derive scalar binding/token metadata from canonical output schemas.
- [x] Derive supported item-collection binding metadata.
- [x] Mark unsupported collection/template shapes truthfully.
- [x] Consolidate response-template compatibility rules into one reusable boundary.
- [x] Add non-mutating Result Template authoring validation.
- [x] Add nested object, optional field, items-template and invalid-path tests.

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

- [x] The same canonical output schema always yields the same binding catalogue.
- [x] Nested scalar paths generate exact `{{result.values.*}}` tokens.
- [x] Required/optional metadata is correct through nested objects and item schemas.
- [x] Arrays of objects expose supported `itemsPath` + `item` bindings.
- [x] Unsupported collection shapes do not generate invalid item tokens.
- [x] Unknown/object/array scalar-token paths are rejected deterministically.
- [x] Authoring validation and publication reuse the same compatibility logic.
- [x] No tag/binding catalogue is persisted.
- [x] No provider I/O or durable writes occur.

## Validation

- [x] focused ToolResultContract compiler tests
- [x] focused Result Template validation tests
- [x] publication compatibility tests
- [x] renderer regression tests
- [x] targeted lint
- [x] changed-file TypeScript diagnostics
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin COMMERCE-066 or COMMERCE-067.

## Implementation Notes

Keep the compiler independent of Shopify/External provider types. Provider-specific logic should already have produced the canonical output schema before this boundary.

## Completion Report

### Status

Submitted for Architect Review (Attempt 1).

### Files Changed

Changed in `moda-interact-commerce`:

- `src/commerce/tool-authoring/result-template-contract.ts`
- `src/commerce/tool-authoring/agent-contract-validation.ts`
- `src/commerce/tool-definition/response-template-syntax.ts`
- `src/commerce/tool-definition/contracts.ts`
- `src/commerce/tool-definition/publication.ts`
- `src/commerce/execution/renderer.ts`
- `tests/tool-result-contract.test.ts`
- `tests/result-template-authoring.test.ts`

### Work Completed

Implemented a deterministic, non-persisted `ToolResultContract` compiler from the canonical output schema, including nested scalar bindings, exact `result.values` tokens, required/optional metadata, and supported/unsupported collection metadata. Added bounded, non-mutating Result Template validation and reused it from publication and Agent-contract validation. Extracted shared safe token/path syntax for schema and runtime use, preserving renderer fallback and scalar-resolution semantics. Added focused compiler, authoring, publication, and renderer regression coverage.

### Validation Results

Passed:

- `./node_modules/.bin/vitest run tests/tool-result-contract.test.ts tests/result-template-authoring.test.ts tests/agent-contract-validation.test.ts tests/arch021-commerce-tool-contract.test.ts tests/definition-execution.test.ts tests/external-publication.test.ts` — 6 files, 60 tests.
- Targeted ESLint on all eight changed TypeScript files — no errors or warnings.
- Changed-file TypeScript diagnostics on all eight changed files — no errors.
- `git diff --check` and staged-diff whitespace check — passed.

### Deviations

No scope deviations. The temporary `node_modules` symlink used to run local tests was removed before commit.

### Assumptions

The compiler consumes the exact canonical output schema supplied by each caller; provider-specific wrapping remains upstream. Required item-field status is derived from the item schema independently of whether the collection property itself is optional.

### Unresolved Issues

None identified. The dedicated authoring module exports `compileToolResultContract` and `validateResponseTemplateAuthoring`; no UI or persistence was added.

### Architectural Concerns

None identified. Existing renderer behavior and the bounded Commerce result-schema limits remain in force.

### Git / VCS

Task branch:
  `task/ARCH-021-COMMERCE-063`

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-063`
  parent branch: `task/ARCH-021-COMMERCE-063`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-063`
  implementation branch: `task/ARCH-021-COMMERCE-063`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Implementation repository:
  repository: `moda-interact-commerce`
  commit: `cdf78eb8241d7171e955fe2392db94e337a94129`
  remote branch: `origin/task/ARCH-021-COMMERCE-063`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/commerce/ARCH-021/COMMERCE-063-compile-tool-result-contract.md`
  commit: review-submission commit on `task/ARCH-021-COMMERCE-063`
  remote branch: `origin/task/ARCH-021-COMMERCE-063`
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is accepted.

The implementation satisfies the COMMERCE-063 boundary. `compileToolResultContract(...)` derives a source-neutral, non-persisted authoring contract from the canonical result schema with deterministic scalar bindings, exact `{{result.values.*}}` tokens, required/optional metadata and bounded collection metadata. Unsupported primitive/nested-array collection shapes are represented explicitly rather than guessed.

`validateResponseTemplateAuthoring(...)` is the single bounded, non-mutating Result Template compatibility boundary and is reused by publication and Agent-contract validation. Shared safe token/path helpers are reused by runtime rendering without changing established fallback or scalar-resolution behaviour. No React UI, durable persistence, provider I/O or provider-specific schema walking was introduced.

The submitted validation is sufficient for this bounded task: six focused test files / 60 tests passed, targeted ESLint passed, changed-file TypeScript diagnostics passed for all eight implementation files, and `git diff --check` passed. The full project test suite was not required by the task validation contract.

### Reviewed Files

- `src/commerce/tool-authoring/result-template-contract.ts`
- `src/commerce/tool-authoring/agent-contract-validation.ts`
- `src/commerce/tool-definition/response-template-syntax.ts`
- `src/commerce/tool-definition/contracts.ts`
- `src/commerce/tool-definition/publication.ts`
- `src/commerce/execution/renderer.ts`
- `tests/tool-result-contract.test.ts`
- `tests/result-template-authoring.test.ts`
- `docs/decisions/commerce/ARCH-021/COMMERCE-063-compile-tool-result-contract.md`

### Validation Reviewed

- Focused Vitest packet: **6 files / 60 tests PASS**.
- Targeted ESLint on the eight changed TypeScript files: **PASS**.
- Changed-file TypeScript diagnostics on the eight changed implementation files: **PASS**.
- `git diff --check`: **PASS**.
- Full project test suite: not run; not required by this task.

### Architecture Conformance

Conformant. The implementation keeps `ToolResultContract` derived/non-durable, centralises Result Template compatibility without duplicating provider-specific schema logic, preserves runtime renderer semantics and stays within the backend/compiler scope assigned to COMMERCE-063.

### Follow-up

COMMERCE-066 and COMMERCE-067 are now Ready because their sole dependency, COMMERCE-063, is Complete. COMMERCE-068 remains Pending until COMMERCE-065, COMMERCE-066 and COMMERCE-067 are all Complete.
