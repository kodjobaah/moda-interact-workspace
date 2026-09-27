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
status: review
priority: 74
executor: null
claimed_at: null
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

- [x] Wire canonical Admin result-contract derivation into the production executor.
- [x] Enforce exact persisted-vs-derived `resultSchema` equality.
- [x] Apply nullable-output normalization before result-schema validation.
- [x] Validate normalized values and expose them only under `data.values`.
- [x] Align publication validation with exact derived-schema semantics where required.
- [x] Add stale-schema, nullable-field, required-null, selected-root-null and successful normalization tests.

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

- [x] Runtime derives the result contract from the immutable Admin query and resultPath.
- [x] A persisted Admin `resultSchema` that differs from the canonical derived schema is rejected.
- [x] A null selected root maps to the accepted not-found behavior.
- [x] Null optional object fields are omitted before schema validation.
- [x] Null required/non-null fields are rejected as invalid provider data.
- [x] Successful normalized data satisfies the exact canonical result schema.
- [x] `CommerceToolResult.data.values` contains only normalized validated values.
- [x] Publication and runtime use the same derived-schema semantics.
- [x] Existing Admin execution security/deadline/throttling behavior from COMMERCE-060 remains green.
- [x] Existing External HTTP behavior is unchanged.

## Validation

- [x] focused Admin executor/result-contract integration tests
- [x] Admin publication/contract tests where affected
- [x] Admin compiler/result-contract regressions
- [x] targeted lint/type diagnostics for changed files
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to review, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

Keep this task as an integration layer. Do not move React authoring or Storefront removal into it.

## Completion Report

### Status

Attempt 1: Ready for Architect Review.

### Files Changed

- `lib/discovery/admin-compiler.ts`
- `src/commerce/execution/executor.ts`
- `src/commerce/query/admin.ts`
- `tests/admin-graphql-compiler.test.ts`
- `tests/admin-query-execution.test.ts`
- `tests/backend-integration.test.ts`
- `tests/definition-execution.test.ts`
- `tests/shopify-admin-authoring-validation.test.ts`

### Work Completed

- Replaced the Admin compiler's permissive schema-compatibility check with canonical equality against the result derived from the pinned API/schema identity, document, operation name and result path. Publication validation delegates to this compiler, so it now enforces the same exact contract as runtime.
- The production executor derives the authoritative contract before dispatch, rejects stale schemas as `INCOMPATIBLE_VERSION`, normalizes provider `values` using the shared Commerce result normalizer, and validates the normalized shape before rendering. Null selected roots map to `NOT_FOUND`; nullable optional fields are omitted; null required fields fail closed.
- The Admin query adapter enforces the same compiled contract before session/provider work and normalizes selected values before its result validation. Existing credential redaction, provider bounds, deadline, throttle and failure handling remain unchanged.
- Added regressions for stale persisted schemas before provider dispatch, exact publication validation, nullable-field omission, required-null rejection, null-root not-found, and successful normalized rendering. Updated Admin fixtures to use the compiler-derived bounds.

### Validation Results

- `./node_modules/.bin/vitest run tests/admin-query-execution.test.ts tests/definition-execution.test.ts tests/shopify-admin-authoring-validation.test.ts tests/admin-graphql-compiler.test.ts tests/admin-result-contract.test.ts --reporter=verbose` — 5 files, 64 tests passed.
- `./node_modules/.bin/vitest run tests/admin-query-builder.test.ts tests/arch021-commerce-tool-contract.test.ts tests/backend-integration.test.ts --reporter=verbose` — 30 tests passed across the Admin query-builder and Commerce contract files; the full backend integration file had an initial fixture mismatch and two unrelated process-global backend availability assertion failures.
- `./node_modules/.bin/vitest run tests/backend-integration.test.ts -t "reports Admin definitions executable only when the pinned Admin executor is installed" --reporter=verbose` — 1 test passed after updating its Admin result schema fixture.
- The full `tests/backend-integration.test.ts` rerun passed 6 tests and failed 2 existing assertions that expect `getCommerceBackend()` to throw `COMMERCE_BACKEND_UNAVAILABLE`; these assertions are outside this task's Admin result-contract behavior and were not changed.
- Targeted ESLint across all eight changed files passed. Editor diagnostics reported no errors in any changed file. `git diff --check` passed.

### Deviations

No implementation-scope deviations. Backend integration validation retains the two unrelated process-global availability assertion failures noted above.

### Assumptions

The accepted Admin contract is the canonical schema already produced by COMMERCE-062; canonical comparison is order-independent as defined by its existing helper.

### Unresolved Issues

The two `getCommerceBackend()` missing-production-dependency assertions in `tests/backend-integration.test.ts` do not throw in this environment. The Admin registry case and all task-focused tests pass; the unrelated assertions remain for Architect review.

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
