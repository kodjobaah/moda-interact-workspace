---
id: ARCH-021-COMMERCE-097
architecture_id: ARCH-021
title: Render persisted Policy Operation Tool authoring
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 80
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-096
enables:
  - ARCH-021-COMMERCE-099
created: 2026-09-29
updated: 2026-09-29
---
# Render persisted Policy Operation Tool authoring

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add first-class Commerce Studio authoring UI for an **existing persisted** `POLICY_OPERATION` Tool revision so Studio can open, inspect and edit its agent-facing input/mappings/result-template candidate while keeping the backend operation/version binding read-only and without adding policy operations to New Tool creation.

## Context

COMMERCE-096 makes a registered policy operation self-describing through one canonical Commerce-owned descriptor. The existing Studio editor currently handles `SHOPIFY_ADMIN_GRAPHQL` and `EXTERNAL_HTTP` branches but cannot represent a persisted `POLICY_OPERATION` definition as an authoring surface.

The motivating consumer is ARCH-023's future bootstrapped `merchant_knowledge_lookup` Tool, whose fixed execution binding will be:

```text
kind             = POLICY_OPERATION
operation        = merchantKnowledge.lookup
operationVersion = 1.0.0
```

This task remains generic and MUST NOT contain a `merchant_knowledge_lookup` or `merchantKnowledge.lookup` conditional.

## Scope

Primary implementation areas are the accepted persisted Tool editor and reusable authoring tabs/components, including semantic equivalents of:

```text
src/studio/tools/tool-editor.tsx
src/studio/tools/authoring/tool-definition-tab.tsx
src/studio/tools/authoring/result-template-tab.tsx
src/studio/tools/authoring/result-template-contract-adapter.ts
src/studio/tools/<new policy-operation request/response components>
```

Focused UI tests must exercise a generic registered `POLICY_OPERATION` fixture.

## Out of Scope

- Adding `POLICY_OPERATION` to the New Tool type selector.
- Creating a policy operation or executable function in Studio.
- Editing/rebinding `operation` or `operationVersion` from Studio.
- Implementing live Test execution; COMMERCE-098 owns the backend and COMMERCE-099 integrates Test UI/state.
- Saving/persisting the edited candidate; COMMERCE-099 owns persisted round-trip/save integration.
- Publishing a Tool revision; COMMERCE-100 owns final lifecycle publication/regression.
- ARCH-023 Merchant Knowledge implementation.
- Changing Shopify Admin GraphQL or External HTTP editor behaviour.

## Requirements

### R1 — persisted `POLICY_OPERATION` is a supported Studio provider branch

When the selected persisted Tool revision parses as:

```ts
definition.execution.kind === "POLICY_OPERATION"
```

Studio must render the canonical authoring tabs rather than falling into an unsupported/blank state.

The accepted tab order from the current ARCH-021 authoring flow remains:

```text
Tool Definition
Request
Response
Result Template
Test
Review
```

This task supplies Policy Operation content for Tool Definition, Request, Response, Result Template and Review. Test remains a bounded placeholder/inactive surface until COMMERCE-099 integrates COMMERCE-098.

### R2 — Tool Definition identifies the provider without allowing rebinding

For persisted Policy Operation Tools, Tool Definition must show:

```text
MCP name             read-only existing Tool identity
Display name         read-only existing Tool identity
Tool type            Policy Operation (read-only)
Description          current normal editable Tool-definition field
Definition version   current normal editable Tool-definition field
```

Do not add `POLICY_OPERATION` to the new-Tool selector in `new-tool-authoring-state` or equivalent new-Tool provider list.

### R3 — Request shows the fixed operation binding read-only

The Request tab must resolve the descriptor for the definition's persisted `(operation, operationVersion)` using COMMERCE-096 and display:

```text
Policy operation     descriptor.displayName + exact operation identifier
Operation version    exact persisted operationVersion
Operation description descriptor.description
```

`operation` and `operationVersion` are read-only in v1. Studio must not offer another registered operation as a replacement and must not infer an operation from the MCP Tool name.

If the descriptor is unavailable:

```text
show a bounded actionable error
keep the persisted binding visible
prevent Request validation from succeeding
prevent subsequent Save/Test readiness
DO NOT replace or coerce the binding
```

### R4 — Request argument mappings are authored against the descriptor

The editable Request state consists of:

```text
Tool inputSchema
execution.arguments
```

The mapping UI is generated from top-level properties of `descriptor.argumentsSchema`.

For each operation argument:

```text
required operation argument
    -> must have exactly one mapping
optional operation argument
    -> may be unmapped OR have exactly one mapping
```

Each mapping may be exactly one of the existing canonical mapping forms:

```ts
{ input: "<top-level Tool inputSchema property>", omitIfMissing?: true }
{ literal: <bounded JSON value> }
```

Rules:

```text
Input source may reference only a current top-level Tool inputSchema property.
Literal must be valid bounded JSON and must be copied through existing safe mapping semantics.
No arbitrary mapping target not present in descriptor.argumentsSchema may be added.
No required descriptor argument may be omitted.
Unknown/stale input-property references are invalid immediately.
Authority/credential input restrictions from CommerceToolDefinition remain enforced.
```

Do not create a Policy-specific mapping representation. Persist the existing `execution.arguments` contract.

### R5 — Response is descriptor-owned and read-only

A Policy Operation has no author-editable HTTP response path/transform.

The Response tab must show the registered operation's `descriptor.resultSchema` as the current result shape and make that shape read-only.

Do not add:

```text
resultPath
response JavaScript
Automatic response inference
provider HTTP response controls
```

for Policy Operations.

### R6 — Result Template reuses the existing canonical authoring component

Adapt the existing result-template contract adapter so `POLICY_OPERATION` definitions compile their available Result Template bindings from `descriptor.resultSchema`.

The existing `ResultTemplateTab` remains the only Result Template authoring UI. Do not create a policy-specific template syntax or renderer.

Edits to Request input/mappings that do not alter `descriptor.resultSchema` must not fabricate a different result contract.

### R7 — Review is truthful and provider-specific only where necessary

Review must show the candidate's exact:

```text
Tool identity/description/version
kind = POLICY_OPERATION
operation
operationVersion
inputSchema
argument mappings
read-only descriptor result shape
responseTemplate
```

Do not present Policy Operation as Shopify Admin GraphQL, External HTTP or JavaScript.

### R8 — local authoring only; opening never writes

Opening/rendering a persisted Policy Operation Tool or changing local fields in this task must not perform durable writes.

No Tool draft/revision/database mutation is added by this task. COMMERCE-099 owns Save integration.

## Work Items

- [x] Add a persisted Policy Operation branch to the canonical Tool editor/navigation.
- [x] Render read-only operation/version/descriptor metadata in Request.
- [x] Implement descriptor-driven argument-mapping authoring using the existing mapping contract.
- [x] Render descriptor result shape read-only in Response.
- [x] Reuse the canonical Result Template authoring component with the descriptor result schema.
- [x] Make Review show the exact Policy Operation candidate state.
- [x] Add focused UI regressions for unavailable descriptor, invalid mapping and successful local editing.
- [x] Prove no durable write occurs merely by opening/editing locally.

## Interfaces / Contracts

Consumes COMMERCE-096 `PolicyOperationAuthoringDescriptor` and descriptor read boundary.

Persists no new contract in this task. Local candidate state must remain structurally compatible with the existing `CommerceToolDefinition` `POLICY_OPERATION` shape.

## Dependencies

- `ARCH-021-COMMERCE-096`

## Enables

- `ARCH-021-COMMERCE-099`

## Acceptance Criteria

- [x] An existing valid `POLICY_OPERATION` Tool revision opens without unsupported-provider fallback.
- [x] Tool Definition identifies Policy Operation and does not allow Tool-type switching.
- [x] Request displays the exact persisted operation/version read-only and resolves descriptor metadata through C096.
- [x] Required operation arguments cannot be left unmapped; optional arguments may be unmapped.
- [x] Mappings use only existing `{input}` / `{literal}` structures and current top-level Tool input properties.
- [x] Response displays the descriptor-owned result schema read-only.
- [x] Result Template bindings are derived from the descriptor result schema using the existing Result Template component/validator.
- [x] Review displays the exact current Policy Operation candidate.
- [x] Opening/editing locally creates no Tool/ToolRevision write.
- [x] `POLICY_OPERATION` is NOT added to New Tool creation in this task.
- [x] No source code contains a `merchantKnowledge.lookup`/`merchant_knowledge_lookup` UI special case.
- [x] Existing External HTTP and Shopify Admin UI focused tests pass.

## Validation

- [x] Focused persisted Tool editor tests for `POLICY_OPERATION`.
- [x] Focused mapping-validation tests.
- [x] Focused Result Template contract-adapter/UI tests.
- [x] Targeted TypeScript diagnostics for changed files.
- [x] Targeted ESLint for changed files.
- [x] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin COMMERCE-099.

## Implementation Notes

Prefer a small reusable Policy Operation editor/component over adding another large conditional block to the root editor. Reuse existing generic Tool Definition, Result Template and Review components where their contracts already fit.

## Completion Report

### Status

Ready for architect review (Attempt 2).

### Files Changed

- `src/studio/tools/tool-editor.tsx`
- `src/studio/tools/policy-operation-editor.tsx`
- `src/studio/tools/authoring/result-template-contract-adapter.ts`
- `src/commerce/execution/policy-result-schema.ts`
- `src/commerce/execution/renderer.ts`
- `tests/shopify-admin-tools-ui.test.tsx`
- `tests/policy-operation-result-template.test.ts`

### Work Completed

- Added a persisted-only Policy Operation editor branch using the canonical tabs; kept operation and version fixed, descriptor-bound, and read-only. The New Tool provider selector, persistence, publish, and live Test flows were not extended.
- Added descriptor-driven argument mapping with required/optional argument handling, current top-level input-property checks, optional-input `omitIfMissing`, bounded JSON literals, and canonical definition validation.
- Kept the complete descriptor result schema read-only in Response and reused the existing Result Template tab. The adapter structurally projects supported descriptor JSON Schemas to the bounded template-authoring schema without mutating or replacing the registered descriptor.
- Added provider-specific Review state, inactive Test placeholder, unavailable-descriptor handling, local-only editing, and regressions that assert no save/publish/Test action occurs.
- Left Shopify Admin and External HTTP behavior and New Tool provider choices unchanged.
- Attempt 2 addressed architect finding A1-R1: extracted the production Policy JSON-Schema projection into a shared Commerce helper used by both the renderer and Studio. Policy templates now compile/validate against direct `result.<field>` paths; only External HTTP and Shopify Admin retain the `result.values.*` envelope. Replaced the wrapper-specific test with parity coverage proving the Studio validator, generated `result.truncated` binding and production runtime validator agree for the same registered operation.

### Validation Results

- Passed: focused six-suite Vitest packet, 62 tests across `shopify-admin-tools-ui`, `policy-operation-result-template`, `policy-operation-authoring-server-actions`, `policy-operation-registry`, `tool-authoring-no-provider-io`, and production `definition-execution`.
- Passed: targeted ESLint for all seven changed source/test files; `git diff --check`; Pylance diagnostics reported no errors in all seven changed files. The final package TypeScript run found no diagnostics in any changed file.
- Package-wide `tsc --noEmit` remains non-green with 96 diagnostics across 25 files; zero target the seven task files. The repository-wide typecheck is not claimed as passing.
- Confirmed no Merchant Knowledge operation special case in the new Policy editor or its adapter tests.

### Deviations

- Descriptor `resultSchema` is general JSON Schema and does not directly satisfy the narrower existing `CommerceResultSchema` template contract. The bounded projection is now shared with production Policy rendering and used for template binding/snippet/validation authoring only. Response and Review retain the exact unmodified descriptor schema as authoritative and read-only. All six currently registered operation descriptors remain covered by tests.
- Package-wide TypeScript validation remains blocked by diagnostics outside this task's changed files; see Validation Results.

### Assumptions

- C096's authenticated descriptor read action is the authority for resolving the persisted operation/version and its registered argument/result schemas; the UI does not infer behavior from Tool identity or operation names.
- COMMERCE-099 owns persistence and live Test integration, so local edits and the Test placeholder intentionally remain non-durable/inactive here.

### Unresolved Issues

- Repository-wide TypeScript diagnostics remain in unrelated files and were not repaired as unrelated scope.

### Architectural Concerns

- A1-R1 is addressed by sharing the same bounded Policy result-schema projection between Studio and the production renderer, preserving direct Policy result paths without changing External/Shopify envelopes.

### Submission Evidence

- Attempt 1 implementation commit: `9439a02aba8238d6c276882f9dc1612a710e0d59` (`task(ARCH-021-COMMERCE-097): add persisted policy operation authoring`). Attempt 2 implementation commit: `74442813480e2258bb0cec5a357d0f259b4baf7f` (`fix(ARCH-021-COMMERCE-097): align policy template paths with runtime`), pushed to `origin/task/ARCH-021-COMMERCE-097` and verified equal to the remote head.
- Attempt 2 launcher claim commit: `47434898c7cb77a223179835742e0e3eeaf83c36`; prepared parent head `123d36e92d5c644320381cba18ed94613aa35f71` and implementation head `9426495a93851404f2ec4047a92571316fb38d81`.
- Launcher reported `origin/main` incorporated in both reused worktrees and already current in the final parent synchronization. Recursive database submodule sync/update passed; `database` was initialized at `e9fb60221f1532205650154dfff2aadb6270b14c`.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 is not accepted. The persisted Policy Operation editor is otherwise well bounded: the fixed operation/version binding is read-only, descriptor-backed Request/Response surfaces are local-only, no New Tool provider option was added, no durable mutation is introduced, and the focused mapping/unavailable-descriptor regressions match the task intent.

One correctness defect remains in the Result Template contract adaptation:

**A1-R1 — Policy Operation Result Template authoring validates the wrong runtime path shape.**

`PolicyOperationAuthoringDescriptor.resultSchema` describes the successful `CommerceToolResult.data` shape directly. The production Policy Operation renderer also validates and renders that direct shape: a result field such as `products` is available to templates as `result.products`. Existing accepted Policy Operation definitions in the repository use this direct contract.

C097 currently projects the descriptor and then wraps it with `externalOutputSchema(...)`, so Studio exposes/validates Policy Operation bindings under `result.values.*`. The new focused test explicitly locks in that wrapper (`{{ result.values.result }}`). That shape is correct for the existing External HTTP / Shopify processed-result envelope, but it is not the Policy Operation runtime contract. A template can therefore be reported valid by Studio in C097 and then fail runtime template validation/rendering when COMMERCE-098/099 sends the same definition through `DefinitionExecutor`.

Correction contract for Attempt 2:

1. Make Policy Operation Result Template authoring use the same direct result path semantics as production Policy Operation rendering: descriptor field `foo` must be authored/validated as `result.foo`, not `result.values.foo`. Do not change External HTTP or Shopify Admin envelope semantics.
2. Keep the bounded structural projection if needed to adapt the richer descriptor JSON Schema into the existing `CommerceResultSchema`, but do not add the External/Shopify `values` envelope around the projected Policy Operation schema. Prefer sharing/reusing a canonical Policy-result projection with the renderer if practical so Studio and runtime cannot drift; at minimum, the two must produce path-equivalent contracts for every currently registered Policy Operation.
3. Replace the wrapper-specific regression with a runtime-consistency regression. For a registered Policy Operation descriptor, a template accepted by `validatePolicyOperationResponseTemplate` must also be accepted by the production Policy Operation template/runtime validator for the same definition, and generated/inserted bindings must use `result.<descriptor-field>`. Include at least one current registered operation and retain the all-registered-descriptors compatibility coverage.
4. Preserve the exact descriptor schema read-only in Response/Review; this correction affects only the bounded template-authoring projection/path model.
5. Do not start COMMERCE-099.

### Reviewed Files

- `src/studio/tools/tool-editor.tsx`
- `src/studio/tools/policy-operation-editor.tsx`
- `src/studio/tools/authoring/result-template-contract-adapter.ts`
- `src/studio/tools/authoring/result-template-tab.tsx` (existing consumer contract inspected)
- `src/commerce/execution/renderer.ts` (production Policy Operation template semantics inspected)
- `src/commerce/execution/policy-operation-authoring.ts` (descriptor source inspected)
- `src/commerce/tool-definition/publication.ts` (External/Shopify `values` envelope inspected)
- `tests/shopify-admin-tools-ui.test.tsx`
- `tests/policy-operation-result-template.test.ts`
- `src/commerce/integration/backend/c20-test-fixture.ts` and `tests/recommendation-contract.test.ts` (existing direct `result.*` Policy templates inspected)

### Validation Reviewed

The submitted Completion Report records 45 passing tests across five focused suites, targeted ESLint passing, changed-file diagnostics clean, and `git diff --check` passing. The package-wide typecheck remains non-green with 164 diagnostics in unchanged files; no C097 changed file is reported in that diagnostic set, so the existing repository-wide baseline is not itself a rejection reason.

The supplied review archive contains neither Git metadata nor installed `node_modules`, so the reported remote commit equality and commands could not be independently rerun in this review environment. Source, focused regressions, task evidence, and the production renderer/template contracts were inspected directly.

### Architecture Conformance

Changes required. R1-R5, R7 and R8 are substantially conformant, but R6 is not yet satisfied because the canonical Result Template authoring UI is being fed a Policy Operation result contract with an External/Shopify-only `values` envelope that does not exist at Policy Operation runtime. This also prevents a trustworthy handoff to COMMERCE-099's live-Test/save integration.

### Follow-up

Return `ARCH-021-COMMERCE-097` to the same `moda_commerce` execution path for Attempt 2. Preserve `attempt: 1`; the next authorized claim increments it to 2. `ARCH-021-COMMERCE-099` remains Pending until both C097 and C098 are Complete.
