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
status: complete
priority: 47
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-037
enables:
  - ARCH-021-COMMERCE-039
created: 2026-09-25
updated: 2026-09-26
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

- [x] Add the serializable initial Tool creation DTO/input contract.
- [x] Add one Tool mutation service method for the atomic lifecycle command.
- [x] Add one named Server Action for that mutation.
- [x] Return the lifecycle result directly without a publication snapshot.
- [x] Extend audit reconciliation to return exact initial Tool/revision identity.
- [x] Preserve actor authorization and no-replay semantics.
- [x] Add focused service/action/reconciliation tests.
- [x] Preserve existing Tool mutation APIs required by existing Tool editing.

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

- [x] One named Server Action creates the Tool and initial draft through one Commerce command.
- [x] The action accepts the complete proposed definition and returns both created IDs.
- [x] Successful initial creation does not call `backend.publication.snapshot()` to build its result.
- [x] ADMIN hierarchy is enforced through the accepted Studio authorization boundary.
- [x] Deterministic errors remain bounded `ToolMutationResult` errors and never become UNCONFIRMED.
- [x] A committed lost-response create can be reconciled to exact `toolId` + `toolRevisionId` from audit metadata/result.
- [x] Reconciliation performs no mutation and no broad Tool-state scan.
- [x] Existing persisted Tool-editing Server Actions remain available.
- [x] No function-valued production React action prop is introduced.

## Validation

- [x] `npm run test:arch021-tool-authoring-common` — 84 passed, 7 files passed.
- [x] Focused action/reconciliation/Studio packet — 31 passed, 3 files passed.
- [x] Changed-file ESLint passed.
- [x] Typecheck rerun: no task-owned `createToolWithInitialDraft` diagnostics; 16 unrelated baseline errors remain.
- [x] Source audit proves successful atomic creation does not use publication `snapshot()` for result reconstruction.
- [x] `git diff --check` passed.

## Stop Condition

After the named atomic mutation and exact audit reconciliation contract are complete, set this task to `review`, complete the Completion Report and STOP. Do not modify `ToolLibrary`/`ToolAuthoringScreen` to consume it; COMMERCE-039 owns browser migration.

## Implementation Notes

Do not broaden this task into a general Studio service redesign. The purpose is one clean initial-create mutation boundary plus the minimum reconciliation change required by that new operation.

The destination Tool editor may perform its normal read after navigation. Avoid paying for a broad publication snapshot inside the mutation merely to return UI data the browser does not need before navigation.

## Completion Report

### Status
Ready for Review

### Files Changed
`moda-interact-commerce/src/studio/contracts.ts`
`moda-interact-commerce/src/commerce/integration/studio/services.ts`
`moda-interact-commerce/src/studio/server-actions.ts`
`moda-interact-commerce/src/studio/server-services.ts`
`moda-interact-commerce/src/studio/tools/reconciliation-server-actions.ts`
`moda-interact-commerce/tests/studio-integration.test.ts`
`moda-interact-commerce/tests/tool-authoring-server-actions.test.ts`
`moda-interact-commerce/tests/tool-operation-reconciliation.test.ts`

### Work Completed
- Preserved the serializable atomic initial-create input/result contracts while keeping the mutation out of broad `StudioServices`.
- Added a callable `createToolWithInitialDraftMutation` and wired the named `createToolWithInitialDraft` Server Action to it.
- Calls the COMMERCE-037 lifecycle operation exactly once and returns its composite result without a publication snapshot.
- Extended exact audit reconciliation to return `toolId` and `toolRevisionId` for committed `CREATE_TOOL` operations.
- Preserved legacy Tool mutation actions and actor authorization/no-replay behavior.
- Added direct named Server Action success and deterministic `CONFLICT` regression coverage.

### Validation Results
- Implementation commit: `1b2f853` pushed to `task/ARCH-021-COMMERCE-038`.
- `npm run test:arch021-tool-authoring-common`: 84 passed, 7 files passed.
- Focused action/reconciliation/Studio packet: 31 passed, 3 files passed.
- Changed-file ESLint: passed.
- `git diff --check`: passed.
- Source audit: atomic creation path contains no `publication.snapshot()` result reconstruction.

### Deviations
The repository typecheck exits nonzero on 16 unrelated baseline diagnostics outside this task (preview imports, agent configuration tests, fixtures, MCP context, and selected-shop-context tests). No task-owned diagnostics for `createToolWithInitialDraft` remain. Focused Vitest, common acceptance tests, changed-file lint, and diff checks pass.

### Assumptions
The COMMERCE-037 lifecycle result is the canonical serializable `{ toolId, toolRevisionId, editVersion, updatedAt }` DTO.

### Unresolved Issues
Full repository typecheck remains subject to the 16 documented unrelated baseline diagnostics; changed-file diagnostics are clean.

### Architectural Concerns

## Architect Review

### Review Status
Accepted — Attempt 2

### Review Notes

#### Attempt 2 review — 2026-09-26

Accepted implementation `1b2f853` and the reconciled Attempt 2 handoff.

Attempt 2 closes the complete Attempt 1 correction contract:

- the named `createToolWithInitialDraft` Server Action now calls a real `createToolWithInitialDraftMutation` runtime method;
- the mutation invokes the COMMERCE-037 lifecycle command exactly once and returns the bounded `{ toolId, toolRevisionId, editVersion, updatedAt }` result directly;
- the atomic create result is not reconstructed through `publication.snapshot()`, `listTools()` or `getTool()`;
- atomic creation remains mutation-only rather than widening the broad `StudioServices` contract, eliminating the task-owned `StudioResult` / `ToolMutationResult` and `InMemoryStudioServices` type failures;
- direct tests invoke the actual exported Server Action and prove both successful composite identity and deterministic `CONFLICT` propagation;
- exact audit-only reconciliation still returns `toolId` + `toolRevisionId` for the matching committed operation without mutation replay, Tool-name lookup or first-DRAFT scanning;
- existing persisted Tool mutation actions remain intact; no COMMERCE-039 browser authoring or Phase-2 gating work leaked into this task.

Accepted validation evidence:

```text
ARCH-021 common Tool-authoring packet: 84 passed
focused Server Action/reconciliation/Studio packet: 31 passed
changed-file ESLint: passed
git diff --check: passed
typecheck: 16 unrelated documented baseline diagnostics; zero COMMERCE-038-owned diagnostics
```

Implementation commit: `1b2f853`. Submitted parent report handoff: `a9b38d8c`. The developer reported both parent and implementation worktrees clean. Exact launcher preparation fields were not retained in the supplied snapshot, so none are invented here; this does not justify another implementation attempt because the implementation, runtime boundary and requested correction proofs are complete.

COMMERCE-038 is Complete. COMMERCE-039 remains Pending because `ARCH-021-COMMERCE-021` is still `status: review`; COMMERCE-022 and COMMERCE-038 are now Complete, so COMMERCE-021 is the sole remaining dependency gate.

#### Attempt 1 review — 2026-09-26

Reviewed submitted implementation `27c3bc7` against the COMMERCE-038 contract and the attached task-worktree snapshot. Preserve the parts that are already architecturally correct:

- `InitialToolCreationInput` / `InitialToolCreationResult` establish the bounded serializable composite contract;
- the Commerce-backed atomic-create service path authorizes through `requireStudioPlatformRole('ADMIN')`, calls `backend.publication.createToolWithInitialDraft(...)` directly and does not reconstruct the result through `publication.snapshot()`;
- reconciliation remains read-only, origin-checked, ADMIN-authorized and exact-operation scoped;
- committed `CREATE_TOOL` reconciliation can return `toolId` + `toolRevisionId` directly from the audit row/result without Tool-name or broad publication scans;
- existing Tool edit/publish/enable actions remain present;
- no browser authoring or Phase-2 gating work was pulled into this task.

Attempt 1 is not accepted because the new named Server Action is not connected to an actual runtime mutation method, the new contract introduces task-owned TypeScript errors, and the required direct Server Action proof is absent. The attached handoff snapshot also does not contain the reported final task-report state.

The following is the complete authoritative Attempt 2 correction contract. Keep the correction narrow; do not implement COMMERCE-039 browser authoring.

##### A1-R1 — make the named atomic Server Action callable at runtime

Current code declares:

```ts
createToolWithInitialDraftMutation: (...) => Promise<ToolMutationResult<InitialToolCreationResult>>
```

in `ToolMutationServices`, and the named Server Action executes:

```ts
service().createToolWithInitialDraftMutation(...)
```

but `createCommerceStudioServices()` does **not** return a `createToolWithInitialDraftMutation` property. It instead returns:

```ts
async createToolWithInitialDraft(input) { ... }
```

with a `ToolMutationResult` shape. Therefore the named action currently attempts to call `undefined`; `toolMutation(...)` catches that failure and converts it to `INTERNAL_ERROR`. The atomic operation cannot be invoked through the new public Studio action.

Correct the boundary so the property the Server Action calls exists at runtime and calls `backend.publication.createToolWithInitialDraft(...)` exactly once. Follow the established COMMERCE-020 split between the broad Studio service shape and Tool mutation envelope rather than relying on an incompatible intersection.

A valid correction may either:

1. add a real `createToolWithInitialDraftMutation` implementation alongside any intentionally retained `StudioServices` method; or
2. keep atomic creation exclusively on the Tool-mutation/named-Server-Action boundary and remove the unnecessary broad `StudioServices` member, typing the named action from `InitialToolCreationInput` directly.

Whichever shape is chosen, there MUST NOT be one method that is typed as `StudioResult<InitialToolCreationResult>` while actually returning `ToolMutationResult<InitialToolCreationResult>`.

Preserve:

```text
requireStudioPlatformRole('ADMIN')
exact input forwarding
one backend lifecycle call
direct composite result
no publication snapshot/listTools/getTool result reconstruction
```

##### A1-R2 — remove the new task-owned TypeScript contract failures

The submitted `tsconfig.tsbuildinfo` records task-owned diagnostics caused by Attempt 1, including:

```text
TS2322
createToolWithInitialDraft implementation returning ToolMutationResult
is not assignable to StudioServices.createToolWithInitialDraft returning StudioResult

TS2420 / TS2741
InMemoryStudioServices incorrectly implements StudioServices:
Property 'createToolWithInitialDraft' is missing
```

These are not baseline diagnostics because they are direct consequences of the COMMERCE-038 contract addition.

Resolve them according to the boundary selected under A1-R1. If `createToolWithInitialDraft` remains part of `StudioServices`, every real implementation of that interface, including `InMemoryStudioServices`, must satisfy the contract without unsafe casts or upgrading an incomplete DRAFT into a published/full definition. If the operation is mutation-only, remove the unnecessary `StudioServices` requirement instead.

Required proof:

```text
no COMMERCE-038-owned TS2322 for createToolWithInitialDraft
no COMMERCE-038-owned TS2420/TS2741 for InMemoryStudioServices
```

Unrelated documented repository baseline diagnostics may remain.

##### A1-R3 — add a direct regression for the named Server Action

Add focused coverage, preferably in:

```text
tests/tool-authoring-server-actions.test.ts
```

or another clearly named focused Server Action test file.

The regression MUST invoke the actual exported:

```ts
createToolWithInitialDraft
```

from `src/studio/server-actions.ts` and prove at minimum:

```text
valid origin
-> exact InitialToolCreationInput forwarded once
-> actual createToolWithInitialDraftMutation service method called once
-> successful ToolMutationResult contains exact toolId + toolRevisionId + editVersion + updatedAt
```

Also prove one deterministic service failure (for example `CONFLICT` or `INVALID_INPUT`) remains the exact bounded Tool mutation error and is not converted to `UNCONFIRMED` or `INTERNAL_ERROR`.

This test must fail if `createCommerceStudioServices()` omits the mutation method or if the named action is wired to the wrong Tool mutation.

##### A1-R4 — preserve and strengthen audit reconciliation proof

Preserve the current reconciliation implementation and existing actor/no-replay/database-error tests. Keep the committed composite-result regression proving exact `toolId` + `toolRevisionId` recovery from the matching audit row.

Do not reintroduce:

```text
publication.snapshot()
listTools()
getTool()
Tool-name lookup
first-DRAFT lookup
mutation replay
```

into reconciliation.

##### A1-R5 — reconcile the durable Attempt 2 task/report state

The attached architect-review snapshot contains:

```yaml
status: in_progress
attempt: 1
executor: copilot
claimed_at: 2026-09-25T23:59:00Z
```

and all Work Items, Acceptance Criteria and Validation checkboxes remain unchecked with Completion Report status `Not Started`. This does not match the conversational claim that parent report `6dff43ce` was already marked review. Architect review must follow the durable submitted snapshot.

Attempt 2 must provide a final snapshot containing the actual pushed report state and reconcile:

```text
Work Items
Acceptance Criteria
Validation
Completion Report status = Ready for Review
files changed
exact validation results
implementation commit
launcher-prepared parent + implementation worktrees
start-of-attempt synchronization evidence
recursive submodule evidence
push parity
clean parent worktree
clean implementation worktree
```

Before handoff set exactly:

```yaml
status: review
attempt: 2
executor: null
claimed_at: null
```

Do not create source churn merely to change an implementation commit when a correction does not require it. Here source/test correction is required by A1-R1 through A1-R3, so return the actual resulting implementation commit.

##### A1-R6 — deterministic validation

Run:

```bash
npm run test:arch021-tool-authoring-common

npm exec vitest run \
  tests/tool-authoring-server-actions.test.ts \
  tests/tool-operation-reconciliation.test.ts \
  tests/studio-integration.test.ts \
  tests/auth-role-requirements.test.ts

npm run typecheck

npm exec eslint \
  src/studio/contracts.ts \
  src/studio/server-actions.ts \
  src/studio/server-services.ts \
  src/studio/tools/reconciliation-server-actions.ts \
  src/commerce/integration/studio/services.ts \
  src/studio/testing/in-memory-studio-services.ts \
  tests/tool-authoring-server-actions.test.ts \
  tests/tool-operation-reconciliation.test.ts \
  tests/studio-integration.test.ts

git diff --check
```

If A1-R1 removes the operation from `StudioServices` and therefore requires no change to `in-memory-studio-services.ts`, it may be omitted from changed-file lint, but the typecheck must still prove no new COMMERCE-038-owned contract diagnostic.

##### Attempt 2 stop condition

Return to architect review only when:

```text
the named createToolWithInitialDraft Server Action calls a real mutation method
AND the atomic backend lifecycle command is invoked exactly once
AND the direct composite result is returned without a broad reread
AND no COMMERCE-038-owned StudioResult/ToolMutationResult type conflict remains
AND no COMMERCE-038-owned StudioServices implementation diagnostic remains
AND the actual named Server Action has focused success + deterministic-error coverage
AND exact audit-only composite reconciliation remains intact
AND existing Tool mutation actions remain intact
AND the final durable task/report snapshot is reconciled and pushed
```

Then set the task to `review`, return control to `moda_architect`, and STOP. Do not begin COMMERCE-039.

### Reviewed Files

- `src/studio/contracts.ts`
- `src/studio/server-actions.ts`
- `src/studio/server-services.ts`
- `src/studio/tools/reconciliation-server-actions.ts`
- `src/commerce/integration/studio/services.ts`
- `src/studio/testing/in-memory-studio-services.ts`
- `tests/tool-authoring-server-actions.test.ts`
- `tests/tool-operation-reconciliation.test.ts`
- `tests/studio-integration.test.ts`
- `tsconfig.tsbuildinfo`
- `docs/decisions/commerce/ARCH-021/COMMERCE-038-expose-atomic-tool-creation-boundary.md`

### Validation Reviewed

- submitted common/focused/ESLint/diff results from the handoff;
- source-level comparison against the pre-COMMERCE-038 snapshot;
- generated TypeScript build-state diagnostics for the new contract boundary;
- direct Server Action caller/service-method wiring;
- reconciliation query/result behavior.

### Architecture Conformance

Accepted. The Studio mutation boundary now conforms to COMMERCE-036/037 atomic creation semantics, COMMERCE-020 Tool mutation/error conventions, exact audit-only reconciliation, repository ownership and the COMMERCE-039 browser-authoring separation.

### Follow-up

COMMERCE-039 remains Pending. Its COMMERCE-022 and COMMERCE-038 dependencies are Complete; ARCH-021-COMMERCE-021 remains the sole unsatisfied dependency while it is in `review`.
