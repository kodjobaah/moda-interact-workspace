---
id: ARCH-021-COMMERCE-096
architecture_id: ARCH-021
title: Expose registered Policy Operation authoring descriptors
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 80
executor: copilot
claimed_at: 2026-09-29T16:58:47Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-095
enables:
  - ARCH-021-COMMERCE-097
  - ARCH-021-COMMERCE-098
created: 2026-09-29
updated: 2026-09-29
---
# Expose registered Policy Operation authoring descriptors

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Make the existing `POLICY_OPERATION` execution kind self-describing for Commerce Studio by attaching one canonical authoring/runtime contract to each registered policy operation and exposing that descriptor through an ADMIN-authorized read boundary, without adding a new execution kind, function runtime or Studio-authored executable code.

## Context

`POLICY_OPERATION` already exists in the canonical `CommerceToolDefinition` contract and the production `DefinitionExecutor`. The current implementation resolves policy adapters through `PolicyOperationRegistry`, while operation input/output validation is held separately by executor-local `POLICY_SCHEMAS`. Commerce Studio currently has no server-owned descriptor it can use to render an existing `POLICY_OPERATION` Tool safely.

ARCH-023 will later register `merchantKnowledge.lookup@1.0.0` and bootstrap a Tool whose definition uses this existing execution kind. ARCH-021 must provide generic Studio support first. This task must not implement Merchant Knowledge or add the `merchantKnowledge.lookup` operation itself.

COMMERCE-095 is the current Tool-authoring/navigation frontier. This task starts only after that accepted authoring surface is present so later tasks build on one canonical editor flow.

## Scope

Primary implementation boundaries:

```text
src/commerce/execution/ports.ts
src/commerce/execution/executor.ts
src/commerce/integration/backend/executors.ts
src/commerce/integration/backend.ts
src/commerce/**/<policy-operation registration/catalogue module>
src/studio/tools/<policy-operation descriptor read boundary>
```

Focused tests must cover the canonical policy-operation registry/descriptor behaviour and the Studio descriptor read boundary.

## Out of Scope

- Adding a new Tool execution kind such as `FUNCTION` or `LOCAL_FUNCTION`.
- Authoring JavaScript/TypeScript functions in Commerce Studio.
- Adding `CommerceFunction`, `CommerceFunctionRevision` or equivalent database tables.
- Implementing `merchantKnowledge.lookup` or any ARCH-023 Merchant Knowledge runtime.
- Adding `POLICY_OPERATION` to the New Tool type selector.
- Changing Tool publication/release semantics.
- Changing Shopify Admin GraphQL or External HTTP execution behaviour.
- Exposing adapters, credentials, tenant context or executable functions to the browser.

## Requirements

### R1 — keep `POLICY_OPERATION` as the only execution mechanism

The existing persisted definition shape remains authoritative:

```ts
{
  kind: "POLICY_OPERATION";
  operation: PolicyOperation;
  operationVersion: PolicyOperationVersion;
  arguments: Record<string, Mapping>;
}
```

Do not create a second function/execution abstraction. A policy operation remains Moda-owned source code registered at application startup and invoked by `DefinitionExecutor`.

### R2 — one registration owns runtime validation and Studio authoring metadata

Extend the canonical policy-operation registration so each `(operation, operationVersion)` registration owns all of the following:

```ts
type PolicyOperationAuthoringDescriptor = {
  operation: PolicyOperation;
  operationVersion: PolicyOperationVersion;
  displayName: string;
  description: string;
  argumentsSchema: SubsetSchema;
  resultSchema: CommerceResultSchema;
};

type PolicyOperationRegistration = {
  operation: PolicyOperation;
  operationVersion: PolicyOperationVersion;
  inputValidator: z.ZodType;
  outputValidator: z.ZodType;
  authoring: PolicyOperationAuthoringDescriptor;
  adapter: PolicyOperationAdapter;
};
```

Mechanically equivalent names are allowed only where required by repository-local naming, but there must be one registration object per operation/version containing the adapter, runtime validators and authoring descriptor.

`argumentsSchema` describes the object accepted **after** Tool argument mapping. `resultSchema` describes the successful `CommerceToolResult.data` shape available to Result Template authoring.

Do not maintain a second Studio-only operation metadata list.

### R3 — registry resolution is canonical for runtime and authoring

The policy registry must expose semantic equivalents of:

```ts
resolve(operation, operationVersion)
  -> registered adapter + runtime validators + authoring descriptor | null

describe(operation, operationVersion)
  -> deeply immutable PolicyOperationAuthoringDescriptor | null
```

`DefinitionExecutor` must resolve the registration once and use that registration's `inputValidator`, `adapter` and `outputValidator` for `POLICY_OPERATION` execution.

Remove the executor-local `POLICY_SCHEMAS` ownership after all existing registrations have moved to the canonical registrations. Do not leave two independent maps that must be updated together.

### R4 — existing policy operations remain behaviourally unchanged

Every policy operation that is valid on the accepted C095 base must be represented by exactly one registration with the same operation identifier/version, adapter and runtime input/output validation semantics.

This task must not rename existing operation identifiers or change their business behaviour.

A duplicate `(operation, operationVersion)` registration must fail deterministically at registry creation.

### R5 — descriptor data is bounded and browser-safe

The descriptor returned to Studio may contain only:

```text
operation
operationVersion
displayName
description
argumentsSchema
resultSchema
```

It must not expose:

```text
adapter/function references
Zod validator objects
shopId
shop domain
access tokens
headers
credentials
environment variables
conversation/grant context
```

Return cloned/deeply immutable JSON-compatible schema data so browser mutation cannot alter the runtime registry.

### R6 — ADMIN-authorized descriptor read boundary

Add one Commerce Studio server-side read operation equivalent to:

```ts
getPolicyOperationAuthoringDescriptor({
  operation,
  operationVersion,
}):
  | { status: "AVAILABLE"; descriptor: PolicyOperationAuthoringDescriptor }
  | { status: "UNAVAILABLE" };
```

Requirements:

```text
ADMIN authorization uses the existing Studio authorization boundary.
The operation/version are validated through the canonical Tool contract types.
The result is derived only from the current server-side registry.
Unknown/unregistered operation/version returns UNAVAILABLE.
No fallback/synthetic descriptor is created.
No database write occurs.
```

### R7 — do not make policy operations dynamically executable merely because metadata exists

The descriptor is an authoring/read contract, not authority. Runtime execution still requires:

```text
valid published/pinned Tool definition
normal conversation/tool grant
current registered operation/version
normal DefinitionExecutor authorization/context
operation-specific business validation
```

Descriptor availability alone never grants execution.

## Work Items

- [ ] Extend the canonical policy-operation registration with runtime validators and the exact bounded authoring descriptor.
- [ ] Move existing policy-operation runtime input/output validation ownership out of executor-local `POLICY_SCHEMAS` into registrations.
- [ ] Add canonical `resolve`/`describe` registry behaviour with deterministic duplicate rejection.
- [ ] Populate descriptors for every policy operation valid on the accepted base without changing business behaviour.
- [ ] Add the ADMIN-authorized descriptor read boundary.
- [ ] Add focused registry/executor/descriptor tests.
- [ ] Record exact changed files and validation evidence in the Completion Report.

## Interfaces / Contracts

Produces the Commerce-local `PolicyOperationAuthoringDescriptor` contract and the ADMIN-authorized descriptor read boundary consumed by COMMERCE-097 and COMMERCE-098.

This is a repository-local Commerce authoring contract. It is not a cross-service Shared contract.

## Dependencies

- `ARCH-021-COMMERCE-095`

## Enables

- `ARCH-021-COMMERCE-097`
- `ARCH-021-COMMERCE-098`

## Acceptance Criteria

- [ ] `POLICY_OPERATION` remains the existing Tool execution kind; no new function execution type exists.
- [ ] Each accepted existing operation/version has exactly one canonical registration containing adapter, runtime validators and authoring descriptor.
- [ ] `DefinitionExecutor` uses the canonical registration validators and adapter; executor-local `POLICY_SCHEMAS` no longer owns a duplicate operation contract.
- [ ] Duplicate operation/version registration fails deterministically.
- [ ] `describe()` returns the exact bounded descriptor for a registered operation/version and `null`/`UNAVAILABLE` for an unknown pair.
- [ ] Studio's server read boundary is ADMIN-authorized and performs no durable write.
- [ ] Descriptor output contains no executable adapter, secret, credential or tenant/grant state.
- [ ] Existing policy-operation execution tests retain their accepted behaviour.
- [ ] Shopify Admin GraphQL and External HTTP execution tests show no regression attributable to this task.

## Validation

- [ ] Focused policy registry/executor tests.
- [ ] Focused Studio descriptor server-action/read-boundary tests.
- [ ] Targeted TypeScript diagnostics for changed files.
- [ ] Targeted ESLint for changed files.
- [ ] `git diff --check`.

If repository-wide typecheck/build is already required by the current ARCH-021 baseline/task convention, run it and classify only pre-existing diagnostics according to `docs/development-baseline.md`; this task must introduce no changed-file diagnostic.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin COMMERCE-097 or COMMERCE-098.

## Implementation Notes

Keep the descriptor boundary server-owned. Do not serialize functions or Zod objects to the browser. Do not solve this task by adding a hard-coded Studio dropdown/list independent of the runtime registrations.

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
