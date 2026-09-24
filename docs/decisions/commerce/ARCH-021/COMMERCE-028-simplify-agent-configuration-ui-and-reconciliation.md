---
id: ARCH-021-COMMERCE-028
architecture_id: ARCH-021
title: Simplify Agent Configuration UI and make failures reconcilable
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-025
  - ARCH-021-COMMERCE-026
  - ARCH-021-COMMERCE-027
  - ARCH-021-COMMERCE-011
  - ARCH-021-COMMERCE-012
  - ARCH-021-COMMERCE-013
  - ARCH-021-COMMERCE-014
enables:
  - ARCH-021-COMMERCE-029
created: 2026-09-24
updated: 2026-09-24
---

# Simplify Agent Configuration UI and make failures reconcilable

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`


## Objective

Remove Phase-2 action-bundle/replay/unknown-state UI machinery from Agent Configuration, consume named Server Actions directly, and provide explicit user-visible error plus read-only reconciliation for requests whose response is genuinely unconfirmed.

## Context

Current Agent Configuration components generate operation IDs, retain executable operation closures, interpret `kind:'unknown'`, and offer "Check original operation" because domain services stored replay results in audit metadata. The new service contract retains operationId only as an atomic audit receipt and exposes a read-only reconciliation action.

## Scope

Primary files:

```text
app/agent-configuration/page.tsx
components/production-studio-page.tsx
components/studio-workspace.tsx
src/studio/agent-configuration/agent-configuration-screen.tsx
src/studio/agent-configuration/platform-model-configuration.tsx
src/studio/agent-configuration/shop-agent-configuration.tsx
src/studio/agent-configuration/platform-prompt-configuration.tsx
src/studio/agent-configuration/prompt-template-library.tsx
src/studio/agent-configuration/*-server-actions.ts
src/studio/agent-configuration/reconciliation-server-actions.ts
tests/*agent-configuration*.test.tsx
```

## Out of Scope

- General Tools/Connections/Features/Release port removal (COMMERCE-029).
- Merchant-facing Agent Configuration UI. The auth boundary exists, but platform/shop configuration UI remains platform-admin controlled in this checkpoint.
- MCP changes.

## Requirements

### R1. No function-valued Agent Configuration action props

Remove production props/types equivalent to:

```text
agentConfigurationActions
agentConfigurationTemplateActions
agentConfigurationPromptActions
ModelConfigurationActions
TemplateConfigurationActions
PromptConfigurationActions
```

Client Agent Configuration components import named Server Actions directly from their `*-server-actions.ts` modules.

Server Components may pass serializable initial DTOs only.

### R2. No generic unknown result UI

Remove service-result handling for:

```text
kind:'unknown'
CONFLICTING_REPLAY
Check original operation
stored invoke() closure
```

Known Server Action results display their exact `code` and bounded `message`.

### R3. Preserve genuine unconfirmed transport state

When a Server Action Promise rejects before the client receives a typed result:

1. do not silently ignore the exception;
2. keep the generated `operationId` plus action label in serializable local state;
3. display a visible `UNCONFIRMED` notice containing a bounded error message;
4. offer `Reconcile`;
5. disable automatic retry until reconciliation completes or the user explicitly abandons the unconfirmed attempt.

Do not store a function/closure in reconciliation state.

### R4. Reconcile behavior

`Reconcile` calls `reconcileAgentConfigurationOperation({operationId})`.

- `committed`: reload canonical DTOs and show "Committed; state refreshed".
- `not-committed`: show "Not committed" and permit retry with a new operationId.
- explicit error: display the returned error and retain reconciliation control where appropriate.
- DB unavailable: keep state unconfirmed; do not falsely classify committed/not committed.

### R5. Explicit database failures

If Server Action returns `DATABASE_UNAVAILABLE`, render that code/message directly. Do not relabel it "outcome unknown".

### R6. Simplified configuration UX

Model and prompt overrides read/write the single `CommerceAgentConfiguration` DTO:

```text
modelId / modelEditVersion
activePromptRevisionId / promptEditVersion
```

Clearing override visibly returns to platform inheritance without deleting/recreating a configuration row.

### R7. Simplified template UX

Consume COMMERCE-026 current-template API. Remove template revision history/draft/publish controls while retaining categories and current promptText editing.

### R8. Existing correctness guards stay

Preserve:

```text
dirty prompt edit guards
stale shop-load isolation
navigation blocking
prompt publish immutability
CAS conflict display
server-validated selected shop
```

## Work Items

- [ ] Remove Agent Configuration action-object props.
- [ ] Import named actions directly in Agent Configuration domain components.
- [ ] Replace replay/unknown UI with explicit errors + R3/R4 reconciliation.
- [ ] Update UI to reduced config/template DTOs.
- [ ] Preserve existing dirty/stale/CAS protections.
- [ ] Update focused UI tests.

## Interfaces / Contracts

Consumes COMMERCE-025/026 mutation/reconciliation contracts and COMMERCE-027 platform authorization helpers.

## Dependencies

- ARCH-021-COMMERCE-025
- ARCH-021-COMMERCE-026
- ARCH-021-COMMERCE-027
- ARCH-021-COMMERCE-011
- ARCH-021-COMMERCE-012
- ARCH-021-COMMERCE-013
- ARCH-021-COMMERCE-014

## Enables

- ARCH-021-COMMERCE-029

## Acceptance Criteria

- [ ] No production Agent Configuration function bundle crosses Server -> Client.
- [ ] Known errors are visible with their real codes.
- [ ] Transport-level uncertainty is visible and reconcilable.
- [ ] Reconciliation never replays stored mutation results.
- [ ] A database outage is not mislabeled as a committed/unknown operation.
- [ ] Existing dirty/stale/CAS protections remain.

## Validation

- [ ] model UI focused tests
- [ ] prompt UI focused tests
- [ ] template UI focused tests
- [ ] rejected-Promise -> UNCONFIRMED -> reconcile committed test
- [ ] reconcile not-committed -> retry-enabled test
- [ ] DB unavailable visible error test
- [ ] targeted ESLint/typecheck
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.


## Implementation Notes

"Reconcilable" does not mean "swallow every error into unknown". Typed server errors remain errors. Reconciliation exists for the narrow case where the client did not receive a trustworthy typed outcome.

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
