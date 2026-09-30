---
id: ARCH-021-COMMERCE-036
architecture_id: ARCH-021
title: Create a Tool and its initial draft as one lifecycle operation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 45
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-016
  - ARCH-021-COMMERCE-020
enables:
  - ARCH-021-COMMERCE-037
created: 2026-09-25
updated: 2026-09-26
---

# Create a Tool and its initial draft as one lifecycle operation

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add one Commerce publication lifecycle operation that creates a new `CommerceTool` and its revision-1 `DRAFT` definition atomically under one operation/audit identity, so initial Tool creation can no longer commit a Tool row without its first draft revision.

## Context

The accepted Tool authoring boundary currently exposes two independent mutations:

```text
createTool(...)
    -> CREATE_TOOL

createToolDraft(...)
    -> CREATE_TOOL_DRAFT
```

`src/studio/tools/tool-library.tsx` currently invokes them sequentially. A committed first mutation followed by browser abandonment, navigation, process failure or a failed second mutation can therefore leave a durable Tool with zero revisions.

The intended new Studio flow is different: authoring remains non-durable until the user finishes the new-Tool authoring flow, then one final command creates the Tool plus its first draft. This task establishes that atomic Commerce lifecycle capability only. It does not change Studio UI yet and does not optimize the Prisma storage implementation yet.

The canonical draft definition remains owned by COMMERCE-016. Existing published/draft editing semantics remain unchanged.

## Scope

Primary files:

```text
src/commerce/publication/lifecycle.ts
src/commerce/publication/ports.ts                 # only if a result/input type belongs here
src/commerce/publication/validation.ts            # command schema only if this is the existing command-schema owner
src/commerce/tool-definition/contracts.ts         # consume; change only if required by the existing canonical contract
src/commerce/tool-definition/publication.ts       # consume existing draft validation

tests/commerce-lifecycle.test.ts
tests/fixtures/publication-store.ts                # only if required by lifecycle test support
```

Additional directly affected Commerce publication tests may be changed when required by the new lifecycle operation.

## Out of Scope

- Replacing `PrismaPublicationStorage.transaction()` or `readState()` / `writeState()`; COMMERCE-037 owns the narrow PostgreSQL path.
- Studio service or Server Action exposure; COMMERCE-038 owns that boundary.
- React/new-Tool authoring changes; COMMERCE-039 owns the browser flow.
- Phase 2 tab gating, Next/Back progression, completed-step state or locked tabs.
- Publishing the initial revision.
- Requiring a live Tool test.
- Removing the existing `createTool`, `createToolDraft`, `updateToolDraft` or published-Tool lifecycle methods.
- Database schema/migration changes.
- Capability/Release changes.

## Requirements

### R1 — one explicit initial-creation command

Add one lifecycle operation for initial Tool creation. Use one explicit request contract equivalent to:

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

The exact method/type names may follow repository conventions, but the operation MUST represent the complete initial Tool creation, not a hidden call to `createTool()` followed by a second independent `createToolDraft()` command.

Use the existing `CREATE_TOOL` audit action. Do not add a new Prisma enum value or database migration merely to name the composite operation.

### R2 — canonical definition validation

Before durable state is accepted:

1. validate the submitted definition through the canonical COMMERCE-016 draft-definition validator/schema;
2. require `proposedDefinition.name === name`;
3. preserve all existing draft-definition bounds/security constraints;
4. do not require publication eligibility or a live Tool test;
5. reject malformed input with the existing bounded lifecycle error semantics.

The command creates a structurally valid initial `DRAFT`; it does not publish it.

### R3 — one logical state transition

A successful operation MUST produce both:

```text
Tool
  id: newly allocated Tool id
  name/displayName/description: submitted metadata
  enabled: preserve the current initial-Tool default

ToolRevision
  id: newly allocated revision id
  toolId: created Tool id
  revisionNumber: 1
  editVersion: 1
  status: DRAFT
  definition: exact canonical validated draft definition
```

Return a bounded result containing at least:

```ts
{
  toolId: string;
  toolRevisionId: string;
  editVersion: 1;
  updatedAt: string;
}
```

Do not require a caller to rediscover the created revision by scanning Tool state.

### R4 — one operation/replay identity

The Tool and initial revision are part of the same lifecycle operation and therefore use one `operationId`, one payload hash and one audit/replay result.

The audit/result metadata MUST identify both:

```text
toolId
toolRevisionId
```

An identical replay of the same operation returns the original result and does not create another Tool or revision.

Reuse of the same `operationId` with a different actor, Tool metadata or proposed definition returns the existing `OPERATION_REUSE_CONFLICT` behaviour.

### R5 — atomic rollback semantics

Using the existing lifecycle transaction abstraction for this task, prove that any failure before the operation commits leaves neither the Tool nor the initial revision visible in publication state.

At minimum cover failure:

```text
before audit / operation recording
```

using the existing fixture transaction hooks or equivalent established test mechanism.

COMMERCE-037 will separately prove the same property against the narrow Prisma transaction.

### R6 — existing lifecycle compatibility

Existing operations remain available and semantically unchanged:

```text
createTool
createToolDraft
updateToolDraft
publishToolRevision
```

This task introduces the new atomic capability without opportunistically deleting legacy entry points. Later tasks decide which Studio callers migrate to it.

## Work Items

- [x] Add the initial Tool + draft command schema/type.
- [x] Add the lifecycle operation using the canonical draft-definition validator.
- [x] Create Tool and revision 1 in one lifecycle transaction/state mutation.
- [x] Record one replay/audit result containing `toolId` and `toolRevisionId`.
- [x] Add identical-replay and conflicting-reuse tests.
- [x] Add Tool-name conflict and definition-name mismatch tests.
- [x] Add atomic rollback regression coverage.
- [x] Preserve existing Tool lifecycle operations unchanged.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-016
CommerceToolDraftDefinition
canonical draft-definition validation
```

Preserves:

```text
ARCH-021-COMMERCE-020
operationId / audit reconciliation model
bounded LifecycleError semantics
```

Produces one new Commerce lifecycle command whose result includes both created durable identifiers.

No cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-016
- ARCH-021-COMMERCE-020

## Enables

- ARCH-021-COMMERCE-037

## Acceptance Criteria

- [x] One lifecycle call creates the Tool and revision 1 `DRAFT` together.
- [x] A successful result contains both `toolId` and `toolRevisionId`.
- [x] No successful initial-creation command can produce a Tool with zero revisions.
- [x] The initial revision uses `revisionNumber: 1`, `editVersion: 1` and `status: DRAFT`.
- [x] The canonical draft-definition validator is used and definition name must equal Tool name.
- [x] One operation/audit result records both created identifiers.
- [x] Identical operation replay creates no duplicate Tool/revision and returns the original result.
- [x] Altered operation reuse is rejected deterministically.
- [x] Injected transaction failure leaves neither created object committed in fixture state.
- [x] Existing Tool lifecycle methods and their tests remain valid.
- [x] No database migration is introduced.

## Validation

- [x] `npm run test:arch021-tool-authoring-common`
- [x] focused `tests/commerce-lifecycle.test.ts` initial-create/replay/rollback cases
- [x] targeted TypeScript diagnostics for changed files or `npm run typecheck` when repository baseline permits
- [x] targeted ESLint for changed files or `npm run lint` when repository baseline permits
- [x] `git diff --check`

## Stop Condition

After the lifecycle contract, tests and required validation above are complete, set this task to `review`, complete the Completion Report and STOP. Do not implement the narrow Prisma persistence path, Studio Server Action or browser authoring refactor.

## Implementation Notes

Keep this task deliberately storage-agnostic. It is acceptable for the new lifecycle command to use the existing `PublicationStoragePort.transaction()` temporarily so the business semantics can be reviewed independently. COMMERCE-037 owns removal of the whole-publication-state persistence cost for this new command.

Do not add a `CREATE_TOOL_WITH_INITIAL_DRAFT` Prisma enum value. The business/audit intent remains `CREATE_TOOL`; metadata/result distinguishes the composite result.

## Completion Report

### Status
Ready for Review

### Files Changed
- `src/commerce/publication/lifecycle.ts`
- `tests/commerce-lifecycle.test.ts`

### Work Completed
- Added `createToolWithInitialDraft`, using one `CREATE_TOOL` lifecycle command and transaction for Tool plus revision-one `DRAFT` creation.
- Applied canonical `CommerceToolDraftDefinitionSchema` validation and required the definition name to match the Tool name.
- Returned `toolId`, `toolRevisionId`, `editVersion: 1`, and the Tool `updatedAt` from the single operation.
- Preserved replay/conflict behavior and recorded both created identifiers in one audit/result envelope.
- Added atomic rollback, replay, conflict, mismatch, revision-shape, and legacy compatibility coverage.

### Validation Results
- `npm run test:arch021-tool-authoring-common`: 7 files passed, 81 tests passed.
- Focused `tests/commerce-lifecycle.test.ts`: 34 tests passed.
- Targeted ESLint for changed files: passed with zero warnings.
- `git diff --check`: passed.
- `npm run typecheck`: repository baseline exited 2; no diagnostics referenced task-owned files.
- No database migration, Prisma persistence-path change, Studio Server Action, or browser authoring refactor was introduced.

### Deviations
- The fresh implementation worktree required `npm ci` before validation because dependencies were not materialized; package installation completed successfully with existing peer/engine/audit warnings.

### Assumptions
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-036`, branch `task/ARCH-021-COMMERCE-036`, claim commit `81239640d90371611fd0fafab1750e8339a8154c`, synchronized with its remote branch.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-036`, branch `task/ARCH-021-COMMERCE-036`, implementation commit `4fb736076901639b17b3d2f93061fc4b8c225173`, synchronized with `origin/task/ARCH-021-COMMERCE-036`.
- Recursive database submodule evidence: `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Attempt 2 claim commit: `86ac3dd2490f6f7e65c9e823fe6dced0d1351863`, pushed and synchronized before this report-only correction.
- Parent report branch is clean and local/remote parity was verified after the report-only correction was pushed.

### Unresolved Issues
Repository-wide typecheck remains baseline-bearing outside the task-owned files and was not altered.

### Architectural Concerns
None

## Architect Review

### Review Status
Accepted — Attempt 2

### Review Notes

#### Attempt 2 review — 2026-09-26

Reviewed the preserved implementation `4fb736076901639b17b3d2f93061fc4b8c225173` and the submitted report-only parent handoff `4ac637f0` against the complete Attempt 1 correction contract.

Accepted. Attempt 1 had already established that the implementation is architecturally conformant. Attempt 2 correctly performs only the requested durable-record reconciliation:

- all 8/8 Work Items are checked against the already-reviewed implementation;
- all 11/11 Acceptance Criteria are checked against the already-reviewed implementation/tests;
- all 5/5 required Validation items are reconciled to the recorded Attempt 1 evidence;
- Completion Report status is exactly `Ready for Review`;
- final execution metadata is `status: review`, `attempt: 2`, `executor: null`, `claimed_at: null` before this acceptance;
- the implementation commit remains `4fb736076901639b17b3d2f93061fc4b8c225173`;
- comparison of the submitted Attempt 1 and Attempt 2 workspace snapshots shows that the task markdown is the only changed file; `src/commerce/publication/lifecycle.ts` and `tests/commerce-lifecycle.test.ts` are unchanged.

The accepted implementation therefore remains exactly the lifecycle capability reviewed in Attempt 1: one `CREATE_TOOL` operation creates the Tool plus revision-1 `DRAFT`, validates the canonical draft definition/name relationship, returns both durable identifiers, preserves replay/conflict semantics, and rolls back atomically at the lifecycle transaction boundary.

No additional implementation rerun is required for this report-only correction. The accepted validation evidence remains:

```text
npm run test:arch021-tool-authoring-common
  -> 7 files / 81 tests passed

focused tests/commerce-lifecycle.test.ts
  -> 34 tests passed

targeted ESLint
  -> passed with zero warnings

npm run typecheck
  -> repository baseline exited 2; zero diagnostics in task-owned files

git diff --check
  -> passed
```

`ARCH-021-COMMERCE-036` is Complete. Its direct dependent `ARCH-021-COMMERCE-037` is promoted from Pending to Ready. `ARCH-021-COMMERCE-038` and `ARCH-021-COMMERCE-039` remain dependency-gated.

#### Attempt 1 review — 2026-09-25

Reviewed implementation `4fb736076901639b17b3d2f93061fc4b8c225173` and the submitted Completion Report against the COMMERCE-036 task contract.

The implementation is architecturally conformant in substance and MUST be preserved:

- `createToolWithInitialDraft` is one lifecycle command using the existing `CREATE_TOOL` operation/audit identity;
- the complete proposed DRAFT is parsed by the canonical `CommerceToolDraftDefinitionSchema` and then passed through `validateToolDraftDefinition`;
- definition `name` must equal the immutable Tool `name`;
- one transaction/state mutation creates the enabled Tool plus revision 1 with `editVersion: 1` and `status: DRAFT`;
- the command returns `toolId`, `toolRevisionId`, `editVersion` and `updatedAt` directly;
- the existing generic command boundary includes the complete request in the operation payload hash, replays an identical committed operation, rejects conflicting reuse, and records both created identifiers in one audit result;
- injected pre-audit failure rolls back the Tool, Tool revision, audit and operation record in the fixture transaction;
- the task did not introduce a database migration, Prisma persistence-path change, Studio Server Action, or browser authoring change.

No repository source or test correction is requested from this review. Do not manufacture code churn or a replacement implementation commit solely for Attempt 2.

The task cannot yet be accepted because the durable execution record was returned in `status: review` without reconciling the implementing-agent-owned checklist state required by the task protocol:

```text
Work Items:          0 / 8 checked
Acceptance Criteria: 0 / 11 checked
Validation:          0 / 5 checked
```

The Completion Report also uses:

```text
Attempt 1 implementation complete; returned to architect review.
```

instead of the canonical Completion Report status `Ready for Review`.

This is a report/workflow correction, not an implementation defect. The following is the complete Attempt 2 correction contract.

##### A1-R1 — reconcile Work Items and Acceptance Criteria

Update this task file only as necessary to reconcile the implementing-agent-owned checklist state to the already-submitted implementation evidence.

For each Work Item and Acceptance Criterion:

1. mark it complete only when the Attempt 1 implementation/tests actually prove it;
2. preserve the existing implementation at `4fb736076901639b17b3d2f93061fc4b8c225173`;
3. if any item cannot truthfully be checked from the existing implementation, do not return the task to review — report the concrete implementation gap instead.

The expected result from the reviewed source/tests is that all eight Work Items and all eleven Acceptance Criteria can be checked without source changes.

##### A1-R2 — reconcile Validation and Completion Report status

Reconcile the five Validation checkboxes to the recorded Attempt 1 results:

```text
npm run test:arch021-tool-authoring-common
  -> 7 files / 81 tests passed

focused tests/commerce-lifecycle.test.ts
  -> 34 tests passed

targeted TypeScript / npm run typecheck
  -> repository baseline exited 2; no diagnostic in task-owned files

targeted ESLint
  -> passed with zero warnings

git diff --check
  -> passed
```

Set the Completion Report status exactly to:

```text
Ready for Review
```

Preserve the existing validation detail, baseline qualification, changed-file list, worktree/isolation evidence and implementation commit evidence.

##### A1-R3 — report-only correction; no implementation rework required

No source/test modification is required by this Architect Review. In particular, do not change:

```text
src/commerce/publication/lifecycle.ts
tests/commerce-lifecycle.test.ts
```

solely to create a new implementation commit.

The existing Attempt 1 validation evidence may be reused for this report-only reconciliation. A full test rerun is not required merely because the task markdown is corrected. Run `git diff --check` for the final task/report change and record the result.

If the reconciliation process reveals that any checked claim would be false, stop and report that discrepancy instead of papering over it.

##### A1-R4 — final Attempt 2 handoff state

On the authorized Attempt 2 claim, increment `attempt` exactly once. Before returning to architect review, leave exactly:

```yaml
status: review
attempt: 2
executor: null
claimed_at: null
```

Record the final parent report commit/push parity and clean parent/implementation worktree state. The implementation commit may remain `4fb736076901639b17b3d2f93061fc4b8c225173` when no source change is needed.

`ARCH-021-COMMERCE-037` remains gated and MUST NOT start until COMMERCE-036 is architect-accepted Complete.

### Reviewed Files

- `docs/decisions/commerce/ARCH-021/COMMERCE-036-create-tool-with-initial-draft-atomically.md`
- `moda-interact-commerce/src/commerce/publication/lifecycle.ts`
- `moda-interact-commerce/src/commerce/publication/ports.ts`
- `moda-interact-commerce/src/commerce/publication/validation.ts`
- `moda-interact-commerce/src/commerce/tool-definition/contracts.ts`
- `moda-interact-commerce/tests/commerce-lifecycle.test.ts`

### Validation Reviewed

- Inspected the actual lifecycle implementation and focused regression additions from the submitted handoff snapshot.
- Reviewed the submitted common-suite result: 81/81 passed.
- Reviewed the submitted focused lifecycle result: 34/34 passed.
- Reviewed the submitted targeted ESLint and `git diff --check` results as clean.
- Reviewed the submitted TypeScript result as baseline-only outside task-owned files.
- Confirmed the command remains on the existing storage-agnostic lifecycle transaction boundary; the narrow Prisma path remains correctly deferred to COMMERCE-037.
- Confirmed no schema/migration change is required by the reviewed implementation.

### Architecture Conformance

Accepted. The implementation conforms to the COMMERCE-036 lifecycle scope and the Attempt 2 durable task/report state now conforms to the execution protocol. The narrow PostgreSQL persistence optimization remains correctly deferred to COMMERCE-037.

### Follow-up

`ARCH-021-COMMERCE-037` is promoted to `ready`. COMMERCE-038 and COMMERCE-039 remain dependency-gated.
