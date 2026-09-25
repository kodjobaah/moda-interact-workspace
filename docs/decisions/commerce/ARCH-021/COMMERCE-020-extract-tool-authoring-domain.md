---
id: ARCH-021-COMMERCE-020
architecture_id: ARCH-021
title: Extract Tool authoring domain onto named Server Actions
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 32
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-016
  - ARCH-021-COMMERCE-005
  - ARCH-021-COMMERCE-006
  - ARCH-021-COMMERCE-027
  - ARCH-021-COMMERCE-029
enables:
  - ARCH-021-COMMERCE-021
  - ARCH-021-COMMERCE-022
created: 2026-09-23
updated: 2026-09-25
---

# Extract Tool authoring domain onto named Server Actions

## Architecture

Architecture ID: ARCH-021

Architecture document: `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator: moda_architect

## Objective

Move the existing Tools library/editor orchestration out of `components/studio-workspace.tsx` into a dedicated Tool-authoring domain that consumes named Server Actions and serializable DTOs, while preserving accepted Tool behavior and adding explicit, UI-reconcilable mutation uncertainty without swallowing deterministic errors.

## Context

COMMERCE-029 completed the production React simplification: production Client Components no longer receive function-valued service/port/render props, and tests must mock the same named Server Action modules used by production. COMMERCE-027 completed the hierarchical authorization model.

`StudioWorkspace` still owns most Tool state and still contains generic `runCommand` logic that converts any rejected mutation promise into `kind: 'unknown'`. That behavior is too broad for Phase 3. A real server result such as `DATABASE_UNAVAILABLE`, `FORBIDDEN`, `CAS_CONFLICT` or `LIVE_TEST_REQUIRED` must remain visible. Only a transport interruption/rejected Server Action invocation after dispatch may become client-side `UNCONFIRMED`, and that state must be reconcilable without replaying the mutation.

## Scope

Create/use exactly:

```text
src/studio/tools/tool-authoring-screen.tsx
src/studio/tools/tool-library.tsx
src/studio/tools/tool-editor.tsx
src/studio/tools/contracts.ts
src/studio/tools/reconciliation-server-actions.ts
components/studio-workspace.tsx
src/studio/server-actions.ts                       # existing named Tool actions; change only as required below
src/commerce/integration/studio/services.ts        # Tool error translation only if required
lib/auth/merchant-access.ts                        # consume existing helpers only
tests/tool-authoring-screen.test.tsx
tests/tool-operation-reconciliation.test.ts
tests/studio-workspace.test.tsx
```

Existing specialized modules such as `src/studio/external-http/editor.tsx` and `src/studio/code-response/code-editor.tsx` remain specialized modules. Do not mechanically move them.

## Out of Scope

- Changing persisted Tool definition shape.
- Adding request JavaScript/Admin GraphQL fields.
- Live provider testing.
- Refactoring Feature/Explore/Capabilities/Releases/Shops surfaces.
- Removing publication lifecycle idempotency/replay internals in this task.
- Merchant-owned Tool libraries.

## Requirements

### R1 — exact production React boundary

`StudioWorkspace` may pass only serializable Tool data/context into `ToolAuthoringScreen`, for example:

```text
role
shopId
returnTo
initial Tool list/detail DTOs
externalHttpCatalogue
productionCodePanel flag or equivalent serializable mode
```

It MUST NOT pass:

```text
StudioServices
action bundle
server-created function-valued port
render function
ExternalHttpUiPort function object
```

If `createExternalHttpSamplePort(externalHttpCatalogue)` remains useful for zero-network client-local preview, construct it inside the Tool domain from the serialized catalogue; it must not cross the Server/Client boundary or be accepted as a production prop.

### R2 — exact named Tool Server Actions

Tool components MUST invoke named Server Actions directly. Reuse the existing exports from `src/studio/server-actions.ts` for:

```text
listTools
getTool
createTool
updateTool
createToolDraft
updateToolDraft
publishToolRevision
setToolEnabled
validateToolDefinition
```

Do not introduce a production `ToolPort`, generic `services` object or action-injection prop for tests. Tests mock/configure these named modules.

### R3 — hierarchical authorization at the Tool boundary

Where the Tool Server Action layer performs authorization directly, use exactly:

```text
read/create/update/create draft/update draft -> requireStudioPlatformRole('ADMIN')
publish/enable/disable                  -> requireStudioPlatformRole('SUPER_ADMIN')
```

The lifecycle's existing role enforcement remains authoritative and MUST NOT be weakened. Merchant roles remain denied for the platform Tool library in Phase 3.

Development bypass is consumed through the COMMERCE-027 resolver; no duplicate bypass validation is allowed.

### R4 — exact Tool mutation result

The extracted Tool domain MUST NOT use the generic `StudioWorkspace.runCommand` `catch -> unknown` behavior.

Define in `src/studio/tools/contracts.ts`:

```ts
type ToolMutationCode =
  | 'FORBIDDEN'
  | 'INVALID_INPUT'
  | 'NOT_FOUND'
  | 'CONFLICT'
  | 'CAS_CONFLICT'
  | 'LIVE_TEST_REQUIRED'
  | 'DATABASE_UNAVAILABLE'
  | 'INTERNAL_ERROR';

type ToolMutationResult<T> =
  | { kind: 'ok'; operationId: string; value: T }
  | {
      kind: 'error';
      operationId: string;
      code: ToolMutationCode;
      message: string;
      retryable: boolean;
    };
```

Server-side rules:

1. deterministic lifecycle/auth/validation errors return their exact bounded code;
2. `LIVE_TEST_REQUIRED` from COMMERCE-019 remains identifiable;
3. Prisma `P1001`, `P1002`, `P1008`, `P1017` are `DATABASE_UNAVAILABLE`, `retryable: true`;
4. unexpected errors are logged with the approved shared structured logger and returned as bounded `INTERNAL_ERROR`;
5. no deterministic server result is converted to `UNCONFIRMED`/`unknown`.

### R5 — transport uncertainty is client state, not swallowed error

For every Tool mutation:

1. generate one `operationId` before invoking the Server Action;
2. if the Server Action returns `ok` or `error`, display that result exactly and do not enter UNCONFIRMED;
3. only if the Server Action invocation itself rejects/loses its response after dispatch may the client set:

```ts
{
  state: 'UNCONFIRMED',
  operationId,
  label
}
```

4. while UNCONFIRMED, block another Tool mutation and Tool-navigation that would discard the unresolved operation;
5. do not automatically re-call the original mutation.

### R6 — exact reconciliation action

Add `src/studio/tools/reconciliation-server-actions.ts` with:

```ts
type ToolOperationReconciliationResult =
  | { kind: 'committed'; operationId: string; action: string }
  | { kind: 'not-committed'; operationId: string }
  | {
      kind: 'error';
      operationId: string;
      code: 'FORBIDDEN' | 'DATABASE_UNAVAILABLE' | 'INTERNAL_ERROR';
      message: string;
    };
```

The action MUST:

1. verify mutation origin;
2. call `requireStudioPlatformRole('ADMIN')`;
3. validate `operationId` through existing `OperationIdSchema`;
4. query `CommerceAuditEvent` by exact `operationId` and current Commerce environment;
5. allow development bypass/SUPER_ADMIN to reconcile any matching Tool operation;
6. for PLATFORM_ADMIN require matching `actorAdminId` when the audit row has one;
7. perform no mutation and never replay the original command;
8. return `DATABASE_UNAVAILABLE` explicitly for Prisma connectivity codes;
9. log unexpected errors server-side and return `INTERNAL_ERROR` without clearing client UNCONFIRMED state.

Client behavior:

```text
committed      -> reload canonical Tool/detail state, clear UNCONFIRMED
not-committed  -> clear UNCONFIRMED; retry is allowed only as a new mutation/new operationId
error          -> keep UNCONFIRMED visible and show exact error
```

### R7 — behavior-neutral extraction

Before COMMERCE-021/022 add new authoring fields, preserve existing:

```text
dirty guards
locked/pending behavior
U06/U14 navigation
connection revision selection
revision history
saved-vs-unsaved identity
existing labels/actions
```

The extraction itself must not change Tool definition serialization.

### R8 — focused validation

`tests/tool-operation-reconciliation.test.ts` MUST prove:

- explicit `DATABASE_UNAVAILABLE` is rendered and is not UNCONFIRMED;
- explicit FORBIDDEN/CAS/CONFLICT remain visible;
- rejected action invocation creates UNCONFIRMED with the original operationId;
- committed reconciliation reloads canonical state;
- not-committed reconciliation permits a new operationId retry;
- reconciliation DATABASE_UNAVAILABLE keeps UNCONFIRMED visible;
- PLATFORM_ADMIN cannot reconcile another admin's audit row;
- PLATFORM_SUPER_ADMIN can reconcile it;
- no original mutation is replayed by reconciliation.

## Work Items

- [ ] Extract Tool library/editor components and state.
- [ ] Make the Tool domain consume named Server Actions and serializable props only.
- [ ] Add explicit Tool mutation-result classification.
- [ ] Add audit-based Tool operation reconciliation.
- [ ] Remove Tool usage of generic StudioWorkspace catch-to-unknown behavior.
- [ ] Add behavior-equivalence and reconciliation tests.

## Interfaces / Contracts

Consumes accepted COMMERCE-005/006 Tool behavior, COMMERCE-016 definition contracts, COMMERCE-027 role hierarchy and COMMERCE-029 React/Server Action boundary.

Produces the Tool UI/mutation/reconciliation boundary extended by COMMERCE-021/022.

## Dependencies

- ARCH-021-COMMERCE-016
- ARCH-021-COMMERCE-005
- ARCH-021-COMMERCE-006
- ARCH-021-COMMERCE-027
- ARCH-021-COMMERCE-029

## Enables

- ARCH-021-COMMERCE-021
- ARCH-021-COMMERCE-022

## Acceptance Criteria

- [ ] Tool-specific state/action code is no longer owned by StudioWorkspace.
- [ ] Production Tool components receive no function-valued server/test dependency props.
- [ ] Tool actions use the accepted platform-role hierarchy.
- [ ] Deterministic Tool errors remain visible and are never rewritten to generic unknown.
- [ ] Transport uncertainty is UI-reconcilable without mutation replay.
- [ ] Existing Tool authoring behavior is unchanged before COMMERCE-021/022.
- [ ] Unrelated Studio surfaces are not refactored.

## Validation

- [ ] focused `tests/tool-authoring-screen.test.tsx`
- [ ] `tests/tool-operation-reconciliation.test.ts`
- [ ] existing `tests/studio-workspace.test.tsx`
- [ ] `npm run test:arch020-external-tools-ui`
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

Set task to `review`, return Completion Report and STOP. Do not add Phase 3 request/Admin authoring fields in this task.

## Implementation Notes

This is the Tool-domain continuation of the accepted COMMERCE-029 simplification, not a wholesale workspace rewrite. The terminal simplification system test remains Ready and intentionally does not gate this implementation task.

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
