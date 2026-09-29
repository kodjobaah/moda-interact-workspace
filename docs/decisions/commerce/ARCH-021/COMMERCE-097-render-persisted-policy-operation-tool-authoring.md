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
status: pending
priority: 80
executor: null
claimed_at: null
attempt: 0
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

- [ ] Add a persisted Policy Operation branch to the canonical Tool editor/navigation.
- [ ] Render read-only operation/version/descriptor metadata in Request.
- [ ] Implement descriptor-driven argument-mapping authoring using the existing mapping contract.
- [ ] Render descriptor result shape read-only in Response.
- [ ] Reuse the canonical Result Template authoring component with the descriptor result schema.
- [ ] Make Review show the exact Policy Operation candidate state.
- [ ] Add focused UI regressions for unavailable descriptor, invalid mapping and successful local editing.
- [ ] Prove no durable write occurs merely by opening/editing locally.

## Interfaces / Contracts

Consumes COMMERCE-096 `PolicyOperationAuthoringDescriptor` and descriptor read boundary.

Persists no new contract in this task. Local candidate state must remain structurally compatible with the existing `CommerceToolDefinition` `POLICY_OPERATION` shape.

## Dependencies

- `ARCH-021-COMMERCE-096`

## Enables

- `ARCH-021-COMMERCE-099`

## Acceptance Criteria

- [ ] An existing valid `POLICY_OPERATION` Tool revision opens without unsupported-provider fallback.
- [ ] Tool Definition identifies Policy Operation and does not allow Tool-type switching.
- [ ] Request displays the exact persisted operation/version read-only and resolves descriptor metadata through C096.
- [ ] Required operation arguments cannot be left unmapped; optional arguments may be unmapped.
- [ ] Mappings use only existing `{input}` / `{literal}` structures and current top-level Tool input properties.
- [ ] Response displays the descriptor-owned result schema read-only.
- [ ] Result Template bindings are derived from the descriptor result schema using the existing Result Template component/validator.
- [ ] Review displays the exact current Policy Operation candidate.
- [ ] Opening/editing locally creates no Tool/ToolRevision write.
- [ ] `POLICY_OPERATION` is NOT added to New Tool creation in this task.
- [ ] No source code contains a `merchantKnowledge.lookup`/`merchant_knowledge_lookup` UI special case.
- [ ] Existing External HTTP and Shopify Admin UI focused tests remain green or show only documented pre-existing baseline failures unrelated to changed files.

## Validation

- [ ] Focused persisted Tool editor tests for `POLICY_OPERATION`.
- [ ] Focused mapping-validation tests.
- [ ] Focused Result Template contract-adapter/UI tests.
- [ ] Targeted TypeScript diagnostics for changed files.
- [ ] Targeted ESLint for changed files.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin COMMERCE-099.

## Implementation Notes

Prefer a small reusable Policy Operation editor/component over adding another large conditional block to the root editor. Reuse existing generic Tool Definition, Result Template and Review components where their contracts already fit.

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
