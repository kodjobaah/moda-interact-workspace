---
id: ARCH-021-COMMERCE-025
architecture_id: ARCH-021
title: Simplify Agent Configuration services and mutation reconciliation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: copilot
claimed_at: 2026-09-24T11:44:32Z
attempt: 1
depends_on:
  - ARCH-021-DATABASE-002
  - ARCH-021-COMMERCE-007
  - ARCH-021-COMMERCE-009
  - ARCH-021-COMMERCE-010
enables:
  - ARCH-021-COMMERCE-028
created: 2026-09-24
updated: 2026-09-24
---

# Simplify Agent Configuration services and mutation reconciliation

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`


## Objective

Replace the Phase-2 selection/pointer/generation/replay service machinery with direct transactional reads/writes over `CommerceAgentConfiguration`, while preserving explicit CAS, audit, and a lightweight UI reconciliation endpoint that never swallows real errors.

## Context

Current model/prompt services use `operationId + payloadHash + stored audit result + replay + generic unknown outcome`. Database connectivity errors can therefore be collapsed into an unhelpful "outcome unknown" state. The replacement must remain reconcilable without treating ordinary PostgreSQL mutations as a distributed-command subsystem.

## Scope

Primary files:

```text
src/commerce/agent-configuration/model-service.ts
src/commerce/agent-configuration/prompt-service.ts
src/commerce/agent-configuration/resolver.ts
src/studio/agent-configuration/model-contracts.ts
src/studio/agent-configuration/prompt-contracts.ts
src/studio/agent-configuration/model-server-actions.ts
src/studio/agent-configuration/prompt-server-actions.ts
src/studio/agent-configuration/effective-server-actions.ts
src/studio/agent-configuration/reconciliation-server-actions.ts   # new
tests/agent-configuration-model.test.ts
tests/agent-configuration-prompt.test.ts
tests/agent-configuration-effective.test.ts
tests/agent-configuration-reconciliation.test.ts                  # new
```

Adjust exact existing filenames only where repository naming differs; do not create parallel service stacks.

## Out of Scope

- Prompt-template service changes (COMMERCE-026).
- Auth.js/merchant authorization (COMMERCE-027).
- React UI changes (COMMERCE-028).
- Tool/connection/release/publication replay behavior.
- MCP authentication.

## Requirements

### R1. Use only the reduced persistence model

Model/default service must use:

```text
CommerceModelCatalogueEntry
CommerceAgentConfiguration
CommerceAuditEvent
```

Prompt service must use:

```text
CommerceAgentPrompt
CommerceAgentPromptRevision
CommerceAgentConfiguration
CommercePromptTemplate
CommerceAuditEvent
```

There must be zero runtime queries against the five dropped Phase-2 models.

### R2. Preserve one operationId only for audit/reconciliation

Every mutation input continues to carry `{ operationId: string; reason: string; ... }`.

`operationId` is a correlation/commit receipt only.

Do not compute or store:

```text
payloadHash
serialized result
metadata.result
metadata.unknown
CONFLICTING_REPLAY
```

The mutation transaction must write the business change and `CommerceAuditEvent(operationId=...)` atomically.

A duplicate `operationId` must never replay a stored result or execute the mutation again. Return explicit error code `OPERATION_ALREADY_COMMITTED`; the caller reconciles via R7.

### R3. Exact mutation result contract

Replace `kind:'unknown'` contracts with:

```ts
type AgentConfigurationMutationResult<T> =
  | { kind: 'ok'; operationId: string; value: T }
  | {
      kind: 'error';
      operationId: string;
      code:
        | 'FORBIDDEN'
        | 'INVALID_INPUT'
        | 'NOT_FOUND'
        | 'CAS_CONFLICT'
        | 'DATABASE_UNAVAILABLE'
        | 'OPERATION_ALREADY_COMMITTED'
        | 'INTERNAL_ERROR';
      message: string;
      retryable: boolean;
    };
```

No generic `unknown` result is allowed from domain/service catch blocks.

### R4. Do not swallow exceptions

Known validation/auth/CAS errors map to their explicit codes.

Recognized Prisma connection/initialization failures map to `DATABASE_UNAVAILABLE` with `retryable=true`.

Unexpected exceptions must be logged through the existing structured logger with bounded correlation metadata and return `INTERNAL_ERROR` with `retryable=false`.

Do not convert an exception to success, empty data, or `unknown`.

### R5. Model operations and CAS

Implement exactly:

```text
listModelCatalogue
createModelCatalogueEntry
updateModelCatalogueEntry
setModelCatalogueEnabled
getPlatformAgentConfiguration
getShopAgentConfiguration
setPlatformModel
setShopModelOverride
clearShopModelOverride
```

CAS rules:

```text
set/clear model -> compare modelEditVersion only
successful model mutation -> increment modelEditVersion exactly once
promptEditVersion unchanged
```

Clearing shop model writes `modelId=NULL`; do not delete configuration row.

### R6. Prompt operations and CAS

Implement/retain exactly:

```text
getPlatformPrompt
getShopPrompt
createPromptDraft
createPromptDraftFromTemplate
updatePromptDraft
publishPromptRevision
setPlatformPrompt
setShopPromptOverride
clearShopPromptOverride
```

`createPromptDraftFromTemplate` reads current `CommercePromptTemplate.promptText`, copies it into the new Agent Prompt DRAFT, and sets `sourceTemplateId`.

CAS rules:

```text
set/clear active prompt -> compare promptEditVersion only
successful prompt mutation -> increment promptEditVersion exactly once
modelEditVersion unchanged
```

Clearing shop prompt writes `activePromptRevisionId=NULL`; do not delete configuration row.

### R7. Add read-only reconciliation action

Add named Server Action:

```ts
reconcileAgentConfigurationOperation({ operationId }): Promise<
  | { kind: 'committed'; operationId: string; action: string }
  | { kind: 'not-committed'; operationId: string }
  | { kind: 'error'; operationId: string; code: 'FORBIDDEN' | 'DATABASE_UNAVAILABLE' | 'INTERNAL_ERROR'; message: string }
>
```

Rules:

1. authorize current Studio principal;
2. look up `CommerceAuditEvent.operationId`;
3. if found and actor is authorized for the event's shop/scope, return `committed` with action only;
4. if absent, return `not-committed`;
5. if database unavailable, return explicit `DATABASE_UNAVAILABLE`;
6. never infer committed state from client memory;
7. never mutate during reconciliation.

The UI re-reads current canonical state after `committed` rather than replaying a serialized result.

### R8. Effective resolver exact rule

Resolve independently:

```ts
modelId = shopConfig?.modelId ?? platformConfig?.modelId ?? null;
promptRevisionId = shopConfig?.activePromptRevisionId ?? platformConfig?.activePromptRevisionId ?? null;
```

Return each source independently as `SHOP | PLATFORM | UNAVAILABLE`.

An explicitly configured but disabled/invalid model or invalid prompt reference fails closed as configuration unavailable; do not silently fall back around a broken explicit override.

## Work Items

- [ ] Remove old table/generation lookups.
- [ ] Remove payload-hash/result replay implementation.
- [ ] Implement R3 explicit error mapping.
- [ ] Implement R5/R6 direct transactional mutations.
- [ ] Implement R7 reconciliation Server Action.
- [ ] Update effective resolver and focused tests.

## Interfaces / Contracts

Consumes DATABASE-002 models directly. No Shared contract changes.

## Dependencies

- ARCH-021-DATABASE-002
- ARCH-021-COMMERCE-007
- ARCH-021-COMMERCE-009
- ARCH-021-COMMERCE-010

## Enables

- ARCH-021-COMMERCE-028

## Acceptance Criteria

- [ ] No Agent Configuration service returns `kind:'unknown'`.
- [ ] Database connectivity errors are visible as `DATABASE_UNAVAILABLE`.
- [ ] No payload hash or stored mutation result is written for these operations.
- [ ] A committed operation is deterministically discoverable by `operationId`.
- [ ] Reconciliation is read-only and UI-oriented.
- [ ] Model/prompt CAS do not interfere with each other.
- [ ] Clearing overrides never deletes configuration rows.

## Validation

- [ ] focused model service tests
- [ ] focused prompt service tests
- [ ] effective resolver tests covering all four platform/shop combinations
- [ ] reconciliation tests: committed / not committed / DB unavailable / unauthorized
- [ ] targeted ESLint/typecheck for changed files
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.


## Implementation Notes

Do not "simplify" by deleting audit/reconciliation. The required simplification is: keep an atomic audit receipt and explicit UI reconciliation, remove generic result replay and swallowed errors.

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
