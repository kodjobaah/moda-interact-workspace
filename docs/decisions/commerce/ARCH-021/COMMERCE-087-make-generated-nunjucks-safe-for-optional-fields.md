---
id: ARCH-021-COMMERCE-087
architecture_id: ARCH-021
title: Make generated Nunjucks templates safe for optional result fields
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 74
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-084
enables:
  - ARCH-021-COMMERCE-083
created: 2026-09-29
updated: 2026-09-29
---

# Make generated Nunjucks templates safe for optional result fields

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Guarantee that a deterministic Nunjucks template generated from a valid Commerce Result contract renders safely for every runtime result value permitted by that contract, including omission of optional fields, without weakening C084's strict renderer or changing C085 editor ownership.

## Context

Manual External live Test exposed this valid sequence:

```text
Request construction   Passed
Connection resolution  Passed
Provider request        Passed
Response processing     Passed
Result validation       Passed
Result rendering        Failed
```

The generated template directly interpolated fields such as:

```nunjucks
Image: {{ item.image }}
Department: {{ item.department }}
Description: {{ item.description }}
```

while the Response contract marked those projected fields optional (`omit if missing`).

The result validator correctly accepts omission of an optional property. The C084 renderer correctly uses strict undefined handling. The mismatch is therefore in the generated-template/runtime-context contract: generated source must not assume that an optional path exists.

This is a C084 generator/renderer correction, not a C085 editor correction.

## Scope

Primary implementation areas:

```text
src/commerce/tool-authoring/result-template-generator.ts
src/commerce/execution/renderer.ts
src/commerce/tool-definition/result-schema.ts          # inspect/reuse only unless a bounded helper belongs here
tests/result-template-generator.test.ts
tests/result-template-renderer.test.ts
tests/external-http-live-test-action.test.ts           # bounded regression where useful
tests/shopify-admin-live-test-action.test.ts           # bounded regression where useful
```

A small pure Commerce-local helper for producing a template-safe render context from a validated result/schema is allowed when it keeps generator/runtime semantics explicit and testable.

## Out of Scope

- C085 CodeMirror/editor UX changes.
- Changing the persisted `nunjucks.v1` template shape.
- Reintroducing Text/Items templates.
- Weakening `throwOnUndefined`.
- Provider Request/Response execution changes.
- Changing C079/C081 authoring lifecycle/Test freshness.
- Shopify Admin Test UI integration; COMMERCE-083.
- Database schema/migration changes.
- Fabricating provider/business values for missing optional fields.
- Broadening C084 grammar except where strictly necessary to implement this optional-field safety contract; return any such grammar change to `moda_architect` before implementation.

## Requirements

### R1 — generated-template runtime-safety invariant

For every canonical `CommerceResultSchema` accepted by the C084 generator:

```text
schema
  -> generateDefaultResultTemplate(schema)
  -> any runtime value accepted by that schema
  -> renderDefinitionResult(...)
```

must not fail merely because a schema-optional property is absent.

Static template validation alone is not sufficient.

### R2 — preserve strict rendering

Keep the C084 renderer's strict undefined protection.

Do not solve this task by globally making undefined values silently stringify.

The render context presented to Nunjucks must have deterministic semantics derived from the already-validated Commerce Result schema/value.

### R3 — missing optional values become template-safe, not fabricated business data

After result-contract validation and before Nunjucks evaluation, normalize only schema-permitted **omitted optional properties** to deterministic template-safe structure.

The normalization:

```text
must not mutate the original processed/provider result
must not change result-contract validity
must preserve every present valid value exactly
must not invent a non-null business value
must be deterministic for the same schema/value
must recurse through nested objects/arrays as required for safe template access
```

A suitable implementation may represent an absent optional scalar as `null`, an absent optional collection as an empty/safe collection context, and an absent optional object using a schema-shaped template-only representation whose descendants remain omission-safe. The exact representation is an implementation detail provided no invalid result is made valid and no non-null business value is fabricated.

### R4 — generator respects effective optionality recursively

Generated source must distinguish required paths from paths that may be absent because:

```text
the property itself is optional
or
any ancestor object/path is optional
```

Required scalar paths may remain direct interpolations.

Optional/effectively-optional scalar output must be guarded so the generated template does not emit a missing value.

Optional/effectively-optional object and collection structures must be emitted in a way that is safe when the structure is absent, including nested optional structures.

Do not introduce a second client-side generator; C085 continues to consume the canonical generator/helper.

### R5 — preserve accepted C084 grammar semantics

Do not reopen the accepted scalar-only equality/comparison rules merely as a shortcut.

If optional object/array safety cannot be expressed with the currently accepted grammar plus a template-safe normalized context, stop and return the grammar gap to `moda_architect` rather than silently broadening `nunjucks.v1`.

### R6 — no valid omission may produce `RESULT_RENDERING_FAILED`

Add runtime regressions proving a generated template renders successfully when optional fields are omitted in every materially distinct supported location:

```text
optional scalar property
multiple optional sibling scalars
optional scalar under a required object
required scalar under an optional object
optional scalar under an optional object
optional object omitted entirely
optional array omitted entirely
optional scalar inside object-list items
nested optional object/list combinations
```

The rendered result may omit corresponding human-readable lines/sections or use the generator's deterministic empty-list fallback, but must not expose `undefined`, `Infinity`, `NaN`, an engine-dependent error, or `RESULT_RENDERING_FAILED`.

### R7 — required fields remain strict

Do not mask an invalid runtime result.

If a required field is absent, result-contract validation must continue to fail before template rendering according to the accepted execution pipeline.

The template-safe normalization is only for omissions already permitted by the canonical result schema.

### R8 — Test and production share the correction

The correction must live at the canonical C084 generator/renderer boundary so:

```text
External live Test
Shopify Admin live Test
production Tool execution
```

all receive identical optional-field safety.

Do not patch only one Test Server Action or one provider.

## Work Items

- [ ] Add a pure deterministic template-safe normalization step for schema-permitted omitted optional properties, or an equivalent bounded renderer-side mechanism satisfying R2/R3.
- [ ] Make the canonical generator propagate effective optionality recursively.
- [ ] Keep required paths direct/strict and optional paths safe.
- [ ] Add nested optional object/list generator fixtures.
- [ ] Add render regressions across all materially distinct omission cases in R6.
- [ ] Add at least one External/Shopify execution-boundary regression proving a valid optional-field omission does not become `RESULT_RENDERING_FAILED`.
- [ ] Confirm no C085 UI/state file is changed.

## Interfaces / Contracts

Consumes:

```text
CommerceResultSchema
validate/normalize result contract from COMMERCE-063/C084
generateDefaultResultTemplate from COMMERCE-084
renderDefinitionResult from COMMERCE-084
```

Produces no new persistent, database or cross-repository contract.

Any new normalization/helper API remains Commerce-local.

## Dependencies

- ARCH-021-COMMERCE-084

## Enables

- ARCH-021-COMMERCE-083

## Acceptance Criteria

- [ ] A generated template renders every schema-valid fixture in the optional-omission matrix without `RESULT_RENDERING_FAILED`.
- [ ] Missing optional scalars never reach Nunjucks as unguarded undefined interpolation.
- [ ] Nested optional objects/arrays are safe recursively.
- [ ] Present valid values are rendered unchanged.
- [ ] Required-field omission still fails result-contract validation before render.
- [ ] Original processed/provider result objects are not mutated by template-safety normalization.
- [ ] No non-null business value is fabricated for an omitted optional property.
- [ ] External Test, Shopify Admin Test and production continue to share one canonical renderer behavior.
- [ ] C084 grammar/runtimeVersion/persisted template shape is unchanged.
- [ ] No C085 UI/state implementation is modified.

## Validation

- [ ] focused generator tests for required vs optional/effective-optional source
- [ ] focused renderer tests for the complete optional-omission matrix
- [ ] focused result-validation regression proving required omissions remain invalid
- [ ] focused External or Shopify live-Test execution regression for optional omission
- [ ] targeted ESLint for changed files
- [ ] changed-file TypeScript diagnostics
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin COMMERCE-083.

## Implementation Notes

Prefer solving optionality at the canonical generator/render-context boundary rather than weakening Nunjucks or duplicating provider-specific behavior.

The runtime result has already passed the canonical Result contract before rendering. The template-safety transformation may therefore rely on that fact but must remain pure and non-mutating.

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

Pending.

### Follow-up

None.
