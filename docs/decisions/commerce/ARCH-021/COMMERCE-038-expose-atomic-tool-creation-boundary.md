---
id: ARCH-021-COMMERCE-038
architecture_id: ARCH-021
title: Expose atomic initial Tool creation through the Studio boundary
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 47
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-037
enables:
  - ARCH-021-COMMERCE-039
created: 2026-09-25
updated: 2026-09-25
---

# Expose atomic initial Tool creation through the Studio boundary

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Expose the COMMERCE-036/037 atomic Tool + initial-draft command as one named Studio mutation with deterministic Tool mutation errors and exact committed-operation reconciliation, without broad publication snapshots or two-step create/draft recovery.

## Context

COMMERCE-020 established named Tool Server Actions and transport-only `UNCONFIRMED` state. The current new-Tool flow still requires two independent mutation APIs:

```text
createToolMutation(...)
createToolDraftMutation(...)
```

The Studio service helper then calls `backend.publication.snapshot()` after mutations to reconstruct returned DTOs. The Tool screen's reconciliation logic also has composite recovery branches that:

```text
reconcile CREATE_TOOL
  -> refresh whole canonical Tool list
  -> find Tool by name
  -> stage second CREATE_TOOL_DRAFT

reconcile CREATE_TOOL_DRAFT
  -> refresh whole canonical Tool list
  -> find first DRAFT revision
```

That is no longer appropriate once initial creation is one atomic operation whose durable audit result already contains both identifiers.

This task creates the server/client mutation contract that COMMERCE-039 will consume. It does not change the React authoring workflow itself.

## Scope

Primary files:

```text
src/studio/contracts.ts
src/studio/tools/contracts.ts
src/studio/server-actions.ts
src/studio/tools/reconciliation-server-actions.ts
src/commerce/integration/studio/services.ts

 tests/tool-authoring-server-actions.test.ts
 tests/tool-operation-reconciliation.test.ts
 tests/studio-integration.test.ts
 tests/auth-role-requirements.test.ts
```

Adjust existing Tool service tests where the new atomic result contract is exercised.

## Out of Scope

- Browser/new-Tool authoring state; COMMERCE-039 owns it.
- Phase 2 tab gating or navigation progression.
- Changing existing persisted draft update/publish behaviour.
- Removing `createToolDraft` for legitimate creation of a later draft from an existing Tool.
- Removing legacy `createTool` before caller inventory proves it is unused.
- Whole-publication storage redesign beyond the COMMERCE-037 command.
- Database migration.
- Live provider calls or publication proof.

## Requirements

### R1 — one named Studio creation mutation

Expose one named Server Action for complete initial Tool creation. The exact export may follow existing naming conventions, for example:

```ts
createToolWithInitialDraft(...)
```

It accepts one serializable payload equivalent to:

```ts
{
  operationId: string;
  reason: string;
  name: string;
  displayName: string;
  description: string;
  proposedDefinition: CommerceToolDraftDefinition;
}
```

It calls the COMMERCE-036/037 Commerce command exactly once.

It MUST NOT implement the operation as sequential calls to existing `createTool` and `createToolDraft` actions.

### R2 — bounded direct creation result

Define one serializable result DTO containing at least:

```ts
{
  toolId: string;
  toolRevisionId: string;
  editVersion: number;
  updatedAt: string;
}
```

Return this result directly from the atomic command.

The successful creation service/action path MUST NOT call:

```text
backend.publication.snapshot()
listTools()
getTool()
```

merely to rediscover the IDs or reconstruct the creation result.

COMMERCE-039 may navigate to the persisted editor and let the destination route perform its normal targeted/canonical read.

### R3 — accepted authorization hierarchy

The initial-create action requires:

```text
requireStudioPlatformRole('ADMIN')
```

through the existing COMMERCE-027/020 hierarchy.

`PLATFORM_ADMIN` and `PLATFORM_SUPER_ADMIN` retain authoring authority. Merchant roles remain denied.

Do not introduce another authorization implementation or development-bypass path.

### R4 — deterministic Tool mutation envelope

Return the existing:

```ts
ToolMutationResult<InitialToolCreationResult>
```

(or repository-equivalent named DTO) and preserve the COMMERCE-020 bounded codes:

```text
FORBIDDEN
INVALID_INPUT
NOT_FOUND
CONFLICT
CAS_CONFLICT
LIVE_TEST_REQUIRED
DATABASE_UNAVAILABLE
INTERNAL_ERROR
```

For this creation command specifically:

- duplicate immutable Tool name -> `CONFLICT`;
- malformed Tool metadata/definition -> `INVALID_INPUT`;
- operation reuse conflict -> `CONFLICT` under the existing Studio mapping;
- database connectivity/transient codes already recognized by COMMERCE-020 -> `DATABASE_UNAVAILABLE`;
- unexpected failures are structured-logged and bounded to `INTERNAL_ERROR`.

A deterministic server error never becomes client `UNCONFIRMED`.

### R5 — exact committed reconciliation result

Extend the existing audit-only reconciliation action so a committed atomic initial create can return its recorded durable identity without a publication snapshot.

For an exact matching committed `CREATE_TOOL` audit whose metadata/result contains the composite identifiers, return a bounded committed result equivalent to:

```ts
{
  kind: 'committed';
  operationId: string;
  action: 'CREATE_TOOL';
  toolId: string;
  toolRevisionId: string;
}
```

The exact public union may preserve generic committed results for other Tool actions, but initial creation must be distinguishable and typed/bounded enough for COMMERCE-039 to navigate directly.

Do not infer committed initial creation by:

```text
Tool name lookup
first DRAFT revision lookup
whole publication snapshot scan
```

### R6 — reconciliation remains read-only and actor-authorized

Preserve COMMERCE-020 reconciliation rules:

1. verify mutation origin;
2. authorize ADMIN hierarchy;
3. validate exact operationId;
4. query only the matching audit operation;
5. PLATFORM_ADMIN cannot reconcile another actor's operation where actor identity is present;
6. SUPER_ADMIN/development-bypass behaviour remains as accepted;
7. never replay the original mutation;
8. deterministic reconciliation errors remain explicit.

### R7 — legacy actions remain available

Do not remove the existing named actions required for editing existing Tools/revisions:

```text
updateTool
createToolDraft
updateToolDraft
publishToolRevision
setToolEnabled
```

`createTool` may remain temporarily for compatibility until COMMERCE-039 migrates the new-Tool UI and a later caller inventory justifies removal.

### R8 — no production function-prop regression

The new creation action must be imported/invoked as a named Server Action through the accepted COMMERCE-029/020 boundary. Do not reintroduce action bundles, service objects or function-valued production React props.

## Work Items

- [ ] Add the serializable initial Tool creation DTO/input contract.
- [ ] Add one Tool mutation service method for the atomic lifecycle command.
- [ ] Add one named Server Action for that mutation.
- [ ] Return the lifecycle result directly without a publication snapshot.
- [ ] Extend audit reconciliation to return exact initial Tool/revision identity.
- [ ] Preserve actor authorization and no-replay semantics.
- [ ] Add focused service/action/reconciliation tests.
- [ ] Preserve existing Tool mutation APIs required by existing Tool editing.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-036
atomic initial Tool lifecycle input/result

ARCH-021-COMMERCE-037
narrow durable persistence/replay semantics

ARCH-021-COMMERCE-020
ToolMutationResult
transport-only UNCONFIRMED model
audit-only reconciliation
authorization hierarchy
```

Produces one named Studio Server Action and one bounded creation-result/reconciliation DTO for COMMERCE-039.

No cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-037

## Enables

- ARCH-021-COMMERCE-039

## Acceptance Criteria

- [ ] One named Server Action creates the Tool and initial draft through one Commerce command.
- [ ] The action accepts the complete proposed definition and returns both created IDs.
- [ ] Successful initial creation does not call `backend.publication.snapshot()` to build its result.
- [ ] ADMIN hierarchy is enforced through the accepted Studio authorization boundary.
- [ ] Deterministic errors remain bounded `ToolMutationResult` errors and never become UNCONFIRMED.
- [ ] A committed lost-response create can be reconciled to exact `toolId` + `toolRevisionId` from audit metadata/result.
- [ ] Reconciliation performs no mutation and no broad Tool-state scan.
- [ ] Existing persisted Tool-editing Server Actions remain available.
- [ ] No function-valued production React action prop is introduced.

## Validation

- [ ] `npm run test:arch021-tool-authoring-common`
- [ ] focused `tests/tool-authoring-server-actions.test.ts`
- [ ] focused `tests/tool-operation-reconciliation.test.ts`
- [ ] focused Studio integration/auth tests affected by the new mutation
- [ ] targeted lint/typecheck with zero new task-owned diagnostics
- [ ] source audit proving successful atomic creation does not use publication `snapshot()` for result reconstruction
- [ ] `git diff --check`

## Stop Condition

After the named atomic mutation and exact audit reconciliation contract are complete, set this task to `review`, complete the Completion Report and STOP. Do not modify `ToolLibrary`/`ToolAuthoringScreen` to consume it; COMMERCE-039 owns browser migration.

## Implementation Notes

Do not broaden this task into a general Studio service redesign. The purpose is one clean initial-create mutation boundary plus the minimum reconciliation change required by that new operation.

The destination Tool editor may perform its normal read after navigation. Avoid paying for a broad publication snapshot inside the mutation merely to return UI data the browser does not need before navigation.

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
