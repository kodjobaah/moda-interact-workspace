---
id: ARCH-021-COMMERCE-070
architecture_id: ARCH-021
title: Enforce derived Shopify Admin result contracts at runtime
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 74
executor: copilot
claimed_at: 2026-09-27T16:23:11Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-060
  - ARCH-021-COMMERCE-062
enables: []
created: 2026-09-27
updated: 2026-09-27
---

# Enforce derived Shopify Admin result contracts at runtime

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Integrate COMMERCE-062's compiler-derived Shopify Admin result contract and nullable-output normalization into COMMERCE-060's production Admin executor so immutable Admin Tool definitions cannot execute with a stale/manually divergent `resultSchema` and successful provider data always reaches canonical `data.values` in the exact shape promised by the published Tool revision.

## Context

COMMERCE-060 deliberately establishes Admin provider execution while retaining the baseline persisted `resultSchema` behavior. COMMERCE-062 independently establishes pure deterministic result-schema derivation/normalization from the Admin GraphQL selection plus `resultPath`.

This task is the narrow integration point between those two backend capabilities. It exists separately so provider/runtime work and compiler work can be implemented/reviewed in parallel.

## Scope

Expected implementation areas include:

```text
src/commerce/execution/
src/commerce/query/ Admin execution integration
lib/discovery/admin-compiler.ts or the COMMERCE-062 result-contract module
src/commerce/tool-definition/publication.ts only where exact derived equality is enforced

tests/query-execution.test.ts
tests/arch021-commerce-tool-contract.test.ts
focused Admin publication/runtime tests
```

## Out of Scope

- React UI changes.
- Explore Shopify.
- External HTTP behavior.
- Result Template authoring.
- Storefront removal.
- New database state.
- Adding a separately persisted `ToolResultContract`.

## Requirements

### R1 — runtime derives the authoritative contract

Before accepting provider output as Tool data, derive the canonical Admin result contract using the same COMMERCE-062 capability used by authoring.

Runtime must not maintain a duplicate interpretation of GraphQL field types/nullability.

### R2 — immutable persisted schema must match exactly

Require the persisted `execution.resultSchema` to be canonically equal to the schema derived from:

```text
apiVersion
schemaHash
document
operationName
resultPath
```

A stale, manually altered or otherwise divergent persisted schema is an incompatible/invalid Tool definition and must fail before its result can be exposed as canonical Tool data.

### R3 — normalize nullable Shopify output before schema validation

After selecting `resultPath`, apply COMMERCE-062's normalization semantics:

```text
selected root null                -> NOT_FOUND
optional/nullable object field null -> omit property
required/non-null field null      -> invalid provider result
```

Do not convert provider `null` to fabricated strings, zero values or empty objects.

### R4 — validate canonical values after normalization

Validate the normalized selected value against the exact derived/persisted result schema and only then assign it to:

```text
CommerceToolResult.data.values
```

`renderDefinitionResult` remains downstream and unchanged in ownership.

### R5 — preserve bounded failures and security

Schema incompatibility or provider-shape violations must use existing bounded Commerce Tool failure semantics and must not expose raw credentials/provider internals.

### R6 — publication/runtime semantics agree

Where publication validates Admin definitions, it must use the same exact derived result-contract equality rather than merely allowing a manually authored compatible superset/subset.

Do not create a second published schema or migration layer.

## Work Items

- [ ] Wire canonical Admin result-contract derivation into the production executor.
- [ ] Enforce exact persisted-vs-derived `resultSchema` equality.
- [ ] Apply nullable-output normalization before result-schema validation.
- [ ] Validate normalized values and expose them only under `data.values`.
- [ ] Align publication validation with exact derived-schema semantics where required.
- [ ] Add stale-schema, nullable-field, required-null, selected-root-null and successful normalization tests.

## Interfaces / Contracts

Consumes:

```text
Admin executor from ARCH-021-COMMERCE-060
Admin result-contract derivation/normalization from ARCH-021-COMMERCE-062
Commerce Tool result/publication contracts
```

Produces no new cross-repository contract.

## Dependencies

- `ARCH-021-COMMERCE-060`
- `ARCH-021-COMMERCE-062`

## Enables

None.

## Acceptance Criteria

- [ ] Runtime derives the result contract from the immutable Admin query and resultPath.
- [ ] A persisted Admin `resultSchema` that differs from the canonical derived schema is rejected.
- [ ] A null selected root maps to the accepted not-found behavior.
- [ ] Null optional object fields are omitted before schema validation.
- [ ] Null required/non-null fields are rejected as invalid provider data.
- [ ] Successful normalized data satisfies the exact canonical result schema.
- [ ] `CommerceToolResult.data.values` contains only normalized validated values.
- [ ] Publication and runtime use the same derived-schema semantics.
- [ ] Existing Admin execution security/deadline/throttling behavior from COMMERCE-060 remains green.
- [ ] Existing External HTTP behavior is unchanged.

## Validation

- [ ] focused Admin executor/result-contract integration tests
- [ ] Admin publication/contract tests where affected
- [ ] Admin compiler/result-contract regressions
- [ ] targeted lint/type diagnostics for changed files
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to review, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

Keep this task as an integration layer. Do not move React authoring or Storefront removal into it.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

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
