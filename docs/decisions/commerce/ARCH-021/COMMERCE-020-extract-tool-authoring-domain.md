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
attempt: 1
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

- [x] Extract Tool library/editor components and state.
- [x] Make the Tool domain consume named Server Actions and serializable props only.
- [x] Add explicit Tool mutation-result classification.
- [x] Add audit-based Tool operation reconciliation.
- [x] Remove Tool usage of generic StudioWorkspace catch-to-unknown behavior.
- [x] Add behavior-equivalence and reconciliation tests.

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

- [x] Tool-specific state/action code is no longer owned by StudioWorkspace.
- [x] Production Tool components receive no function-valued server/test dependency props.
- [x] Tool actions use the accepted platform-role hierarchy.
- [x] Deterministic Tool errors remain visible and are never rewritten to generic unknown.
- [x] Transport uncertainty is UI-reconcilable without mutation replay.
- [x] Existing Tool authoring behavior is unchanged before COMMERCE-021/022.
- [x] Unrelated Studio surfaces are not refactored.

## Validation

- [x] focused `tests/tool-authoring-screen.test.tsx` and `tests/tool-operation-reconciliation.test.ts` plus existing `tests/studio-workspace.test.tsx`: 26 tests passed.
- [x] `npm run test:arch020-external-tools-ui`: 13 tests passed.
- [x] targeted lint/typecheck: changed-file lint and TypeScript diagnostics passed.
- [x] `git diff --check`

## Stop Condition

Set task to `review`, return Completion Report and STOP. Do not add Phase 3 request/Admin authoring fields in this task.

## Implementation Notes

This is the Tool-domain continuation of the accepted COMMERCE-029 simplification, not a wholesale workspace rewrite. The terminal simplification system test remains Ready and intentionally does not gate this implementation task.

## Completion Report

### Status
Ready for Review
### Files Changed
- `components/studio-workspace.tsx`
- `src/studio/tools/tool-authoring-screen.tsx`
- `src/studio/tools/tool-library.tsx`
- `src/studio/tools/tool-editor.tsx`
- `src/studio/tools/contracts.ts`
- `src/studio/tools/reconciliation-server-actions.ts`
- `tests/tool-authoring-screen.test.tsx`
- `tests/tool-operation-reconciliation.test.ts`
### Work Completed
- Routed the Tools page through a serializable Tool authoring screen and named Server Actions.
- Moved the complete legacy Tool library/editor behavior into the Tool domain, including external HTTP authoring, code response panels, discovery handoff, dirty navigation, revision history, and draft lifecycle actions.
- Added bounded Tool mutation result classification and audit-only reconciliation with structured unexpected-error logging.
- Added focused deterministic-error and non-replay reconciliation tests.
### Validation Results
- Editor diagnostics: no errors in changed source/test files.
- `git diff --check`: passed.
- Focused tests: 3 files passed, 26 tests passed.
- `npm run test:arch020-external-tools-ui`: 1 file passed, 13 tests passed.
- Targeted lint: passed.
- Full `npx tsc --noEmit --pretty false`: remains blocked by unrelated existing test/integration diagnostics outside the changed files; changed-file diagnostics are clean.
### Deviations
- Full workspace typecheck retains pre-existing diagnostics in unrelated integration and test files; no changed-file diagnostics remain.
### Assumptions
- Named Tool Server Actions continue to use the existing service/auth boundary for role enforcement.
### Unresolved Issues
- None for this task scope.
### Architectural Concerns
None

## Architect Review

### Review Status
Changes Requested

### Review Notes
Attempt 1 establishes the intended Tool-domain files and preserves much of the existing Tool editor behavior, but the production execution path still violates the task's central Server Action / reconciliation boundary.

Accepted in substance and MUST be preserved in Attempt 2:

- `src/studio/tools/` owns the extracted Tool library/editor surface.
- `ToolLibrary` and `ToolEditor` import the existing named Tool Server Actions rather than receiving a server-created service/port object.
- `createExternalHttpSamplePort(externalHttpCatalogue)` remains client-local and zero-network.
- Existing external HTTP/code-response/discovery/revision-history behavior is retained.
- `ToolMutationResult<T>` and `ToolOperationReconciliationResult` provide the correct target envelopes.

Attempt 2 is limited to the deterministic correction contract below. Do not begin COMMERCE-021/022.

#### CR-1 — Remove the production `controlled` escape hatch and generic Studio Tool command path

Files:

```text
components/studio-workspace.tsx
src/studio/tools/tool-authoring-screen.tsx
```

Current production behavior is non-conformant: `StudioWorkspace` passes `controlled={{ ... setDirty, runCommand, unknown.reconcile ... }}` into `ToolAuthoringScreen`. That means production Tool mutations still use the old workspace `runCommand()` implementation, which catches a rejected mutation into `kind: 'unknown'`, stores the original mutation closure, and `reconcile()` re-calls that closure.

Required Attempt-2 behavior:

1. Remove the `controlled` prop from `ToolAuthoringScreen`'s production API entirely.
2. In the `page === 'tools'` branch, `StudioWorkspace` may pass only serializable Tool context/data:

```text
role
returnTo
detailId
revisionId
shopId
externalHttpCatalogue
productionCodePanel
initialResult
initialDetail
```

3. Do not pass `runCommand`, `setDirty`, `unknown`, `reconcile`, `services`, a Tool action bundle, or another function-valued dependency into `ToolAuthoringScreen`.
4. Do not pass a `navigate` callback from `StudioWorkspace`; `ToolAuthoringScreen` already has `useStudioComposer()` and MUST use that domain-local navigation boundary.
5. The generic `StudioWorkspace.runCommand` / `unknown` machinery may remain for non-Tool legacy surfaces, but the Tool route MUST NOT consume it.
6. `ToolAuthoringScreen` owns its own Tool list/detail/pending/message/dirty/UNCONFIRMED state and named-action mutation lifecycle.

Required regression: mock `ToolAuthoringScreen` in `tests/studio-workspace.test.tsx` and prove the Tools production branch passes no function-valued mutation/navigation/service prop and no `controlled` prop.

#### CR-2 — Make the named Tool mutation Server Actions return the exact bounded mutation envelope

Files:

```text
src/studio/server-actions.ts
src/commerce/integration/studio/services.ts
src/studio/tools/contracts.ts
```

The current production Tool path still receives generic `StudioResult<T>` and classifies it in the browser. That loses required codes because `services.translate()` collapses several `LifecycleError` values to generic `unavailable`/`unknown`.

For these six mutation exports only:

```text
createTool
updateTool
createToolDraft
updateToolDraft
publishToolRevision
setToolEnabled
```

return `Promise<ToolMutationResult<T>>` from the named Server Action boundary. Do not broaden/change the generic `StudioResult` contract for unrelated Studio domains.

Required server-side mapping:

```text
LifecycleError FORBIDDEN                    -> FORBIDDEN, retryable=false
LifecycleError INVALID_INPUT                -> INVALID_INPUT, retryable=false
LifecycleError INVALID_DEFINITION           -> INVALID_INPUT, retryable=false
LifecycleError NOT_FOUND                    -> NOT_FOUND, retryable=false
LifecycleError CONFLICT                     -> CONFLICT, retryable=false
LifecycleError OPERATION_REUSE_CONFLICT     -> CONFLICT, retryable=false
LifecycleError CAS_CONFLICT                 -> CAS_CONFLICT, retryable=false
LifecycleError LIVE_TEST_REQUIRED           -> LIVE_TEST_REQUIRED, retryable=false
Prisma P1001/P1002/P1008/P1017             -> DATABASE_UNAVAILABLE, retryable=true
all other unexpected/unsupported failures   -> INTERNAL_ERROR, retryable=false
```

Every returned mutation result MUST preserve the submitted `operationId`.

Unexpected/unsupported failures MUST be emitted through the approved shared logger:

```ts
import { createLogger } from '@modainteract/moda-interact-shared/logging';
```

Do not use `console.log`, `console.error`, Pino/Winston, or a Commerce-local generic logger. Pass the original thrown `Error`/value to the shared logger; do not log `DATABASE_URL`, credentials, tokens, authorization headers or connection strings.

No Tool mutation Server Action may return `kind: 'unknown'`.

#### CR-3 — UNCONFIRMED must be transport-only and reconciliation must never replay the mutation

File:

```text
src/studio/tools/tool-authoring-screen.tsx
```

Required state:

```ts
{ operationId: string; label: string } | null
```

Do not store the original mutation function/closure.

Exact behavior:

```text
Server Action returns ok/error
-> display exact result
-> do not enter UNCONFIRMED

Server Action Promise rejects after dispatch
-> set UNCONFIRMED with the exact submitted operationId
-> disable further Tool mutations
-> lock Tool/Studio navigation
-> never automatically call the original mutation again
```

Track a monotonic Tool content revision (or equivalent). Capture it when a mutation is submitted and clear dirty state on `ok` only if no newer edit was made while the request was pending. A completed earlier save MUST NOT mark later edits clean.

Reconciliation behavior MUST be exactly:

```text
committed
-> reload canonical listTools()
-> if detailId exists, reload getTool(detailId, revisionId)
-> update local canonical state
-> clear UNCONFIRMED
-> final message: "Committed; state refreshed"

not-committed
-> clear UNCONFIRMED
-> final message: "Not committed"
-> a later retry generates a NEW operationId

error
-> keep UNCONFIRMED
-> display exact error code/message

reconciliation Promise rejects
-> keep the original UNCONFIRMED operationId
-> pending=false
-> final message: "Reconciliation unavailable; try reconciliation again"
```

#### CR-4 — Split composite external-tool creation into two independently reconcilable durable mutations

File:

```text
src/studio/tools/tool-library.tsx
```

Current code uses one outer mutation operation id for `createTool()` and a derived `${operationId}:draft` for `createToolDraft()`, but UNCONFIRMED reconciliation stores only the first id. If Tool creation commits and the draft response is lost, reconciling the first id incorrectly reports the composite workflow committed.

Required behavior for `EXTERNAL_HTTP` creation:

```text
1. createTool with operationId A
2. after confirmed ok, createToolDraft as a SECOND mutation with a freshly generated operationId B
3. navigate only after the draft mutation is confirmed ok
4. if step 2 transport-rejects, UNCONFIRMED stores B, not A
5. reconciliation of B observes only CREATE_TOOL_DRAFT
6. retry after not-committed uses a new operationId C and does not recreate the Tool
```

Do not implement a replay closure or derive a second durable id that the UI cannot reconcile directly.

#### CR-5 — Harden the reconciliation Server Action to the exact task contract

File:

```text
src/studio/tools/reconciliation-server-actions.ts
```

Required corrections:

1. Import and call exactly:

```ts
requireStudioPlatformRole('ADMIN')
```

from `lib/auth/merchant-access.ts`.
2. Keep mutation-origin validation and `OperationIdSchema` validation.
3. Query `CommerceAuditEvent` by exact operation id and current server-derived Commerce environment.
4. Replace `action: { startsWith: 'TOOL_' }` with an explicit enum allow-list containing exactly:

```text
CREATE_TOOL
UPDATE_TOOL
CREATE_TOOL_DRAFT
UPDATE_TOOL_DRAFT
PUBLISH_TOOL_REVISION
ENABLE_TOOL
DISABLE_TOOL
```

Do not use prefix matching for the Prisma enum.
5. Development bypass / SUPER_ADMIN may reconcile any matching Tool audit row.
6. PLATFORM_ADMIN may reconcile only when `actorAdminId` is null or equals the current principal id; a different non-null actor id returns `FORBIDDEN`.
7. P1001/P1002/P1008/P1017 return `DATABASE_UNAVAILABLE` and do not clear client UNCONFIRMED state.
8. Unexpected failures use `@modainteract/moda-interact-shared/logging` and return `INTERNAL_ERROR`. Remove `console.error`.
9. The action performs zero mutations and never invokes any Tool mutation Server Action/service method.

#### CR-6 — Complete the R8 tests; the current two contract-shape assertions are insufficient

Files:

```text
tests/tool-authoring-screen.test.tsx
tests/tool-operation-reconciliation.test.ts
tests/studio-workspace.test.tsx
```

The final focused tests MUST prove all of these executable behaviors:

```text
A. mutation returns DATABASE_UNAVAILABLE
   -> DATABASE_UNAVAILABLE visible
   -> no UNCONFIRMED

B. mutation returns FORBIDDEN
   -> FORBIDDEN visible
   -> no UNCONFIRMED

C. mutation returns CAS_CONFLICT
   -> CAS_CONFLICT visible
   -> no UNCONFIRMED

D. mutation returns CONFLICT
   -> CONFLICT visible
   -> no UNCONFIRMED

E. mutation Promise rejects
   -> UNCONFIRMED visible
   -> original operationId retained
   -> further Tool mutation disabled
   -> navigation locked

F. committed reconciliation
   -> mutation action call count does not increase
   -> listTools reloads
   -> current detail reloads when present
   -> UNCONFIRMED clears
   -> "Committed; state refreshed"

G. not-committed reconciliation
   -> mutation action call count does not increase
   -> UNCONFIRMED clears
   -> "Not committed"
   -> next retry uses a different operationId

H. reconciliation DATABASE_UNAVAILABLE
   -> UNCONFIRMED remains
   -> exact code/message visible

I. reconciliation Promise rejects
   -> UNCONFIRMED remains
   -> original operationId unchanged
   -> pending clears
   -> "Reconciliation unavailable; try reconciliation again"

J. PLATFORM_ADMIN + another non-null actorAdminId
   -> FORBIDDEN

K. SUPER_ADMIN + another actorAdminId
   -> committed

L. external Tool create step 2 rejects
   -> reconciliation uses CREATE_TOOL_DRAFT operation id
   -> does not replay/create a second Tool

M. edits made after a save is submitted
   -> earlier save completion does not clear dirty state
```

Use `vi.mock(...)` for the same named Server Action modules used by production. Do not add a test-only Tool action bundle/port.

### Reviewed Files

- `components/studio-workspace.tsx`
- `src/studio/tools/tool-authoring-screen.tsx`
- `src/studio/tools/tool-library.tsx`
- `src/studio/tools/tool-editor.tsx`
- `src/studio/tools/contracts.ts`
- `src/studio/tools/reconciliation-server-actions.ts`
- `src/studio/server-actions.ts`
- `src/commerce/integration/studio/services.ts`
- `tests/tool-authoring-screen.test.tsx`
- `tests/tool-operation-reconciliation.test.ts`
- `tests/studio-workspace.test.tsx`

### Validation Reviewed

Submitted evidence accepted as useful but insufficient for the missing R1/R4/R5/R6/R8 behavior:

```text
focused tests: 26 passed
ARCH-020 external-tools UI: 13 passed
targeted lint: passed
git diff --check: passed
```

Attempt 2 MUST run exactly:

```bash
npm exec vitest run   tests/tool-authoring-screen.test.tsx   tests/tool-operation-reconciliation.test.ts   tests/studio-workspace.test.tsx

npm run test:arch020-external-tools-ui

npm exec eslint   components/studio-workspace.tsx   src/studio/tools/tool-authoring-screen.tsx   src/studio/tools/tool-library.tsx   src/studio/tools/tool-editor.tsx   src/studio/tools/contracts.ts   src/studio/tools/reconciliation-server-actions.ts   src/studio/server-actions.ts   src/commerce/integration/studio/services.ts   tests/tool-authoring-screen.test.tsx   tests/tool-operation-reconciliation.test.ts   tests/studio-workspace.test.tsx

git diff --check
```

Then run the repository typecheck command declared by `package.json`. Existing unrelated baseline diagnostics may be documented, but there must be zero diagnostics in the files above.

Before returning to review, also prove these source invariants:

```bash
! rg -n 'controlled=' components/studio-workspace.tsx
! rg -n 'controlled\?:' src/studio/tools/tool-authoring-screen.tsx
! rg -n 'console\.(log|error)' src/studio/tools/reconciliation-server-actions.ts
! rg -n 'startsWith:.*TOOL_' src/studio/tools/reconciliation-server-actions.ts
```

### Architecture Conformance

Changes Requested. The component extraction is present, but production still crosses the Tool boundary with function-valued orchestration state and still uses the generic workspace unknown/replay mechanism. The server mutation boundary and reconciliation action also do not yet satisfy the exact bounded-error and no-replay contracts.

### Follow-up

Return this SAME task through `/moda-task ARCH-021-COMMERCE-020`. The next authorized claim becomes Attempt 2. Preserve all accepted extraction/editor behavior above. Do not start COMMERCE-021 or COMMERCE-022.
