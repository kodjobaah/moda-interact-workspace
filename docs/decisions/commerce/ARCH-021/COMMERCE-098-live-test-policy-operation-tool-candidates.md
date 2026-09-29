---
id: ARCH-021-COMMERCE-098
architecture_id: ARCH-021
title: Live-test Policy Operation Tool candidates through DefinitionExecutor
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
# Live-test Policy Operation Tool candidates through DefinitionExecutor

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add one non-durable Commerce Studio live-Test backend for a complete `POLICY_OPERATION` Tool candidate that executes through the normal production `DefinitionExecutor` and registered policy-operation adapter, returning the normal rendered Tool result without bypassing tenant/grant/runtime validation or creating Tool publication proof.

## Context

COMMERCE-096 makes policy registrations canonical and self-describing. The production executor already supports `POLICY_OPERATION`, including argument mapping, operation input validation, adapter execution, output validation, deadline handling and Result Template rendering.

Studio needs a safe candidate-Test boundary equivalent in principle to the accepted External HTTP and Shopify Admin live-Test paths. This task implements the backend only; COMMERCE-099 owns Test-tab UI/freshness integration.

## Scope

Primary implementation boundaries:

```text
src/commerce/tool-authoring/<policy-operation live-test domain service>
src/studio/tools/<policy-operation live-test server action>
src/commerce/integration/backend.ts or existing Studio execution port exposure
focused domain/server-action tests
```

## Out of Scope

- Policy Operation authoring UI; COMMERCE-097 owns it.
- Test-tab UI/state integration; COMMERCE-099 owns it.
- Direct invocation of policy adapters from a Server Action.
- A Studio-only policy executor.
- Durable Tool/ToolRevision writes.
- Publication proof or release membership.
- Implementing new policy operations, including `merchantKnowledge.lookup`.
- Changing existing Policy Operation business logic.

## Requirements

### R1 — exact candidate-Test request contract

Expose one ADMIN-authorized server action/domain boundary equivalent to:

```ts
type PolicyOperationLiveTestInput = {
  definition: CommerceToolDefinition;
  arguments: Record<string, unknown>;
  shopId: string;
};
```

The request must reject before execution when:

```text
definition does not parse through CommerceToolDefinitionSchema
definition.execution.kind !== POLICY_OPERATION
operation/version is not currently registered
shopId is empty/invalid for the selected Studio context
arguments is not a JSON object
serialized arguments exceeds the existing authoring Test input bound (64 KiB unless the accepted common contract has a stricter value)
```

Do not accept shop domain, Shopify token, authorization header, conversation grant id, release id or provider credentials from the browser.

### R2 — selected shop is resolved/authorized server-side

The supplied `shopId` identifies the Studio-selected shop only. The server must apply the existing Studio authorization/selected-shop boundary and construct trusted runtime context server-side.

The browser must not be able to replace trusted:

```text
shop domain
offline session/access token
conversation/tool grant authority
policy credentials/environment
```

with candidate data.

### R3 — execute through the normal DefinitionExecutor

The Test path is exactly:

```text
validated Studio Test request
    -> build bounded trusted test AuthorizedToolCall/context using existing Studio test conventions
    -> existing DefinitionExecutor.execute(...)
    -> registry resolve(operation, operationVersion)
    -> existing mapToolArguments(...)
    -> registration inputValidator
    -> registered PolicyOperationAdapter
    -> registration outputValidator
    -> existing renderDefinitionResult(...)
    -> bounded Test result
```

MUST NOT:

```text
call registration.adapter.execute directly from the Server Action
reimplement mapToolArguments
skip input/output validation
use a fake provider-specific renderer
invent a second response-template implementation
```

### R4 — candidate execution is non-durable

A successful or failed Test performs no write to:

```text
CommerceTool
CommerceToolRevision
CommerceRelease
CommerceConversationGrant
publication proof/audit state that would make the candidate publishable by itself
```

Normal bounded operational telemetry/audit that already applies to Studio live-Test is allowed, but Test must not mutate authoring lifecycle state in PostgreSQL.

### R5 — operation/version is exact and registry-owned

The candidate is executable only when:

```text
definition.execution.operation
+
definition.execution.operationVersion
```

resolve to the current C096 registration.

Unknown/stale/unregistered pairs return a bounded unavailable/incompatible result. Do not fall back to another version and do not choose an operation by Tool name.

### R6 — return the canonical rendered outcome and bounded diagnostics

Return the normal result required by the existing Test UI pattern, including at minimum:

```text
success/failure status
normal CommerceToolResult status/code/retryable fields where applicable
renderedText produced by DefinitionExecutor
bounded diagnostics suitable for Studio
```

Do not return:

```text
adapter/function references
raw credentials
server environment
R2/Shopify/provider secrets
trusted runtime context
```

### R7 — deterministic error classes

Focused tests must prove at least:

```text
invalid candidate definition -> validation failure, no adapter call
non-POLICY_OPERATION candidate -> provider mismatch, no adapter call
unregistered operation/version -> unavailable/incompatible, no adapter call
invalid mapped arguments -> INVALID_INPUT, no adapter call
registered adapter business failure -> canonical CommerceToolResult error
valid registered operation -> canonical rendered success
aborted/deadline call -> canonical DEADLINE behaviour
```

Use existing canonical result/error codes; do not invent Policy-specific business error codes when an existing CommerceToolResult code applies.

## Work Items

- [ ] Add the non-durable Policy Operation candidate-Test domain boundary.
- [ ] Add the ADMIN-authorized Studio Server Action using the selected-shop authorization pattern.
- [ ] Route execution exclusively through `DefinitionExecutor` and C096 registrations.
- [ ] Return canonical rendered result/diagnostics without lifecycle writes.
- [ ] Add deterministic success/failure/security/no-write tests.
- [ ] Record exact validation evidence in the Completion Report.

## Interfaces / Contracts

Consumes:

- canonical `CommerceToolDefinition` / `POLICY_OPERATION` contract;
- COMMERCE-096 policy-operation registry/descriptor registration;
- existing Studio authorization and selected-shop context;
- production `DefinitionExecutor`.

Produces the Commerce-local live-Test action consumed by COMMERCE-099.

## Dependencies

- `ARCH-021-COMMERCE-096`

## Enables

- `ARCH-021-COMMERCE-099`

## Acceptance Criteria

- [ ] A valid Policy Operation candidate can be live-tested without persisting it.
- [ ] Candidate execution goes through `DefinitionExecutor`; the Server Action never calls an adapter directly.
- [ ] The exact registered operation/version is required; there is no fallback or Tool-name inference.
- [ ] Browser input cannot supply trusted shop credentials, grant authority or operation secrets.
- [ ] Invalid mapped input is rejected through the canonical runtime contract before adapter execution.
- [ ] Successful output is validated and rendered through the canonical runtime path.
- [ ] Test creates no Tool revision/publication/release/grant state.
- [ ] Focused failure cases are deterministic and bounded.
- [ ] Existing runtime Policy Operation tests show no regression.

## Validation

- [ ] Focused Policy Operation live-Test domain tests.
- [ ] Focused Studio Server Action authorization/security tests.
- [ ] Explicit no-durable-write assertion.
- [ ] Targeted TypeScript diagnostics for changed files.
- [ ] Targeted ESLint for changed files.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin COMMERCE-099.

## Implementation Notes

Follow the accepted External/Shopify live-Test architecture for authorization, cancellation and result presentation where equivalent. Do not copy provider-specific request/response logic that `DefinitionExecutor` already owns.

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
