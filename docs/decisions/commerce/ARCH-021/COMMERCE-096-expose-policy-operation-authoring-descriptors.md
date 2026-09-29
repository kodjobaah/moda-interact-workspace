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
status: review
priority: 80
executor: null
claimed_at: null
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

- [x] Extend the canonical policy-operation registration with runtime validators and the exact bounded authoring descriptor.
- [x] Move existing policy-operation runtime input/output validation ownership out of executor-local `POLICY_SCHEMAS` into registrations.
- [x] Add canonical `resolve`/`describe` registry behaviour with deterministic duplicate rejection.
- [x] Populate descriptors for every policy operation valid on the accepted base without changing business behaviour.
- [x] Add the ADMIN-authorized descriptor read boundary.
- [x] Add focused registry/executor/descriptor tests.
- [x] Record exact changed files and validation evidence in the Completion Report.

## Interfaces / Contracts

Produces the Commerce-local `PolicyOperationAuthoringDescriptor` contract and the ADMIN-authorized descriptor read boundary consumed by COMMERCE-097 and COMMERCE-098.

This is a repository-local Commerce authoring contract. It is not a cross-service Shared contract.

## Dependencies

- `ARCH-021-COMMERCE-095`

## Enables

- `ARCH-021-COMMERCE-097`
- `ARCH-021-COMMERCE-098`

## Acceptance Criteria

- [x] `POLICY_OPERATION` remains the existing Tool execution kind; no new function execution type exists.
- [x] Each accepted existing operation/version has exactly one canonical registration containing adapter, runtime validators and authoring descriptor.
- [x] `DefinitionExecutor` uses the canonical registration validators and adapter; executor-local `POLICY_SCHEMAS` no longer owns a duplicate operation contract.
- [x] Duplicate operation/version registration fails deterministically.
- [x] `describe()` returns the exact bounded descriptor for a registered operation/version and `null`/`UNAVAILABLE` for an unknown pair.
- [x] Studio's server read boundary is ADMIN-authorized and performs no durable write.
- [x] Descriptor output contains no executable adapter, secret, credential or tenant/grant state.
- [x] Existing policy-operation execution tests retain their accepted behaviour.
- [x] Shopify Admin GraphQL and External HTTP execution tests show no regression attributable to this task.

## Validation

- [x] Focused policy registry/executor tests.
- [x] Focused Studio descriptor server-action/read-boundary tests.
- [x] Targeted TypeScript diagnostics for changed files.
- [x] Targeted ESLint for changed files.
- [x] `git diff --check`.

If repository-wide typecheck/build is already required by the current ARCH-021 baseline/task convention, run it and classify only pre-existing diagnostics according to `docs/development-baseline.md`; this task must introduce no changed-file diagnostic.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin COMMERCE-097 or COMMERCE-098.

## Implementation Notes

Keep the descriptor boundary server-owned. Do not serialize functions or Zod objects to the browser. Do not solve this task by adding a hard-coded Studio dropdown/list independent of the runtime registrations.

## Completion Report

### Status

Ready for Architect Review.

### Files Changed

Implementation changes are in `moda-interact-commerce` on `task/ARCH-021-COMMERCE-096`:

- `src/commerce/execution/ports.ts`
- `src/commerce/execution/policy-operation-authoring.ts`
- `src/commerce/execution/index.ts`
- `src/commerce/execution/executor.ts`
- `src/commerce/execution/renderer.ts`
- `src/commerce/integration/backend.ts`
- `src/commerce/integration/backend/executors.ts`
- `src/commerce/tool-definition/contracts.ts`
- `src/studio/tools/policy-operation-authoring-server-actions.ts`
- `tests/policy-operation-registry.test.ts`
- `tests/policy-operation-authoring-server-actions.test.ts`
- `tests/definition-execution.test.ts`
- `tests/recommendation-contract.test.ts`

### Work Completed

- Added one canonical Commerce policy-operation contract catalogue for all six existing operation/version pairs. Each runtime registration now contains its adapter, input/output Zod validators and bounded authoring descriptor; the descriptor schemas are generated from those same validators.
- Added canonical registry `resolve` and `describe` behavior, deterministic duplicate rejection, and cloned/deeply frozen JSON-compatible descriptor responses. The operation identity is validated by a schema exported from the Commerce Tool contract.
- `DefinitionExecutor` resolves the policy registration once per call and uses its input validator, adapter and output validator. Removed executor-local `POLICY_SCHEMAS` and the duplicate renderer output-validator map; the renderer's policy result schema now starts from the canonical operation contract catalogue.
- Exposed the same active server-side policy registry through `CommerceBackend`; runtime execution, executable-availability checks and Studio reads share that registry instance.
- Added an ADMIN-authorized read-only Studio server action. Invalid or unregistered identities return `UNAVAILABLE`; it exposes only the descriptor fields and performs no database operation.
- Added tests for all six descriptor contracts, nested `discounts.evaluate` arguments, nullable and bounded result fields, descriptor cloning/freezing, duplicates, successful/unavailable reads, authorization denial and unchanged execution.
- Preserved the existing execution kind and all policy operation identifiers, versions, adapters and runtime validator semantics. No Shared, Database, Shopify Admin execution, External HTTP behavior or durable persistence contracts were changed.

### Validation Results

- `./node_modules/.bin/vitest run tests/policy-operation-registry.test.ts tests/policy-operation-authoring-server-actions.test.ts tests/definition-execution.test.ts tests/recommendation-contract.test.ts tests/admin-graphql-compiler.test.ts tests/external-http-executor.test.ts --reporter=dot` — 6 files passed, 54 tests passed.
- `./node_modules/.bin/eslint` on all 13 changed source/test files — passed with no warnings.
- VS Code/Pylance changed-file diagnostics for all 13 changed files — no errors.
- `git diff --check` — passed.
- Additional `tests/backend-integration.test.ts` run: 6 passed, 2 failed. The two failures are existing tests that expect `getCommerceBackend()` to fail when production dependencies are absent; in this environment it initializes successfully. The suite's production policy registration and backend composition tests passed. This did not fail in any changed C096 assertion.
- Generated the local Prisma Client with `./node_modules/.bin/prisma generate --schema database/prisma/schema.prisma` to load the backend integration suite. This changed only ignored worktree dependencies; no schema or submodule pointer changed.

### Deviations

After a concrete schema expressiveness conflict was identified, `moda_architect` confirmed the descriptor contract must use a Commerce-owned JSON-schema type rather than unchanged Shared `SubsetSchema` and current `CommerceResultSchema`. The shared input validator cannot represent the nested `discounts.evaluate` proposal operations; the current result schema cannot represent nullable values or existing collection bounds such as basket lines (100), unknown fields (128), and discount offers (50). Lossy descriptors would misstate accepted arguments/results. The task therefore keeps the descriptor Commerce-local and accurate; no Shared contract was changed.

### Assumptions

The registry's authoring descriptor is the canonical browser-safe authoring contract; the existing Tool definition remains the authority for persisted execution and publication.

### Unresolved Issues

No unresolved implementation issue. The two environment-sensitive backend integration assertions are recorded under Validation Results for Architect review.

### Architectural Concerns

The task's original literal `SubsetSchema` / `CommerceResultSchema` field types could not faithfully express all accepted operation contracts. The Commerce-local descriptor type was approved by `moda_architect` for this attempt and avoids a cross-repository Shared change.

### Prepared Execution Evidence

- Launcher: prepared execution succeeded; dependency gate passed (`ARCH-021-COMMERCE-095` complete); Attempt 1 claim committed and pushed as `7e6356580edb21735a92d35c1bf958688329bf87` by `copilot` at `2026-09-29T16:58:47Z`.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; canonical root was not derived from a previous task worktree.
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-096`, `task/ARCH-021-COMMERCE-096`; launcher head `2bf177c5d2074d7cd42418ff8a8c517657a237ba`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-096`, `task/ARCH-021-COMMERCE-096`; launcher head `229d5548e18cf5ae2b41ead25f97717a625d3a5a`.
- Both remote task branches were already current (`remote_task_branch_fast_forwarded: not-needed`; `origin/main_incorporated: already-current`). Neither shared checkout was switched/mutated and no other task worktree was reused.
- Recursive implementation submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; `database` initialized at `e9fb60221f1532205650154dfff2aadb6270b14c`.
- Implementation commit `e37408b` was pushed on the implementation task branch. Parent report/lifecycle commit `623375c5` was pushed on the mirrored parent task branch. No main branch or submodule pointer was changed.

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
