---
id: ARCH-021-COMMERCE-099
architecture_id: ARCH-021
title: Round-trip and save persisted Policy Operation Tool drafts
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
claimed_at: 2026-09-29T20:55:59Z
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-097
  - ARCH-021-COMMERCE-098
enables:
  - ARCH-021-COMMERCE-100
created: 2026-09-29
updated: 2026-09-29
---
# Round-trip and save persisted Policy Operation Tool drafts

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Integrate the COMMERCE-097 Policy Operation editor and COMMERCE-098 live-Test backend into the canonical persisted-DRAFT authoring-session lifecycle so an existing `POLICY_OPERATION` Tool can be opened, edited in-memory, validated, live-tested, CAS-saved, remounted and restored without changing its fixed operation/version binding.

## Context

COMMERCE-097 supplies the local persisted Policy Operation authoring surfaces. COMMERCE-098 supplies one non-durable production-path live-Test backend. This task connects them to the accepted ARCH-021 persisted authoring-session validation/Test freshness and draft-save lifecycle.

This task is the first task that may durably update an existing Policy Operation DRAFT. It does not create a new Policy Operation Tool identity and does not publish the revision.

## Scope

Primary implementation areas:

```text
src/studio/tools/tool-editor.tsx
src/studio/tools/authoring-session.ts or accepted persisted-session equivalent
src/studio/tools/<policy-operation editor components from C097>
src/studio/tools/<policy-operation live-test action from C098>
existing updateToolDraft / Commerce lifecycle boundary
focused persisted-authoring tests
```

## Out of Scope

- New Tool creation for `POLICY_OPERATION`.
- Rebinding `operation` or `operationVersion`.
- Publishing the DRAFT; COMMERCE-100 owns publication/reopen regression.
- Implementing a policy operation.
- ARCH-023 Merchant Knowledge code.
- Changing External HTTP/Shopify Admin Save/Test semantics.
- Creating another authoring session store or Test freshness model.

## Requirements

### R1 — use the canonical persisted authoring session

Policy Operation authoring must consume the same accepted persisted Tool authoring session/validation ledger/Test freshness model used by the other providers.

Do not introduce Policy-specific authoritative copies of:

```text
dirty
validated
testPassed
testedSnapshot
editVersion
current section
```

Provider-specific transient literal-text/display state may be local, but Save/Test readiness comes from the common authoring session.

### R2 — exact candidate assembly

At every Validate/Test/Save boundary, assemble one current `CommerceToolDefinition` containing exactly:

```text
name                   persisted immutable Tool name
definitionVersion      current editor value
description            current editor value
inputSchema             current Request value
execution.kind          POLICY_OPERATION
execution.operation     original persisted operation
execution.operationVersion original persisted operationVersion
execution.arguments     current Request mappings
responseTemplate        current Result Template value
```

No boundary may build a second stale provider-specific candidate from duplicated buffers.

The original operation/version pair captured from the loaded revision is an invariant for the session. If local state attempts to change either value, validation and Save fail closed.

### R3 — deterministic authored-section validation

The common section ledger must represent current validity for:

```text
Tool Definition
Request
Response
Result Template
```

Policy Operation validation responsibilities are:

```text
Tool Definition
  -> normal identity/description/definitionVersion validation

Request
  -> CommerceToolDefinition inputSchema restrictions
  -> C096 descriptor available for exact operation/version
  -> required/optional operation mappings valid against descriptor.argumentsSchema
  -> literals valid and bounded
  -> mapped Tool input properties exist

Response
  -> exact descriptor.resultSchema is available/current; no editable provider response transform

Result Template
  -> existing Result Template validator against descriptor.resultSchema
```

Changing a value owned by an earlier section must stale the appropriate downstream validation/Test checkpoint using the existing authoring-session rules.

### R4 — one Policy Operation Test tab integrated with common Test freshness

Add one reusable Policy Operation Test surface for persisted DRAFTs.

Before invoking COMMERCE-098 require:

```text
Tool Definition current VALID
Request current VALID
Response current VALID
Result Template current VALID
complete current candidate parses
selected shopId present
Test arguments valid JSON object
Test arguments within the common bounded size
```

Do not automatically validate missing/stale sections when Test is pressed. Show the same owning-step style used by accepted provider flows.

Test lifecycle must use the common equivalent of:

```text
NOT_RUN
RUNNING
PASSED
FAILED
STALE
```

with the common authored-section snapshot. Editing any candidate field after a successful Test makes that Test stale.

### R5 — Test displays canonical C098 output

The Policy Operation Test tab sends exactly:

```ts
{
  definition: currentCandidate,
  arguments: parsedTestArguments,
  shopId: selectedShopId,
}
```

to COMMERCE-098.

Show `renderedText` as the primary successful agent-facing result and bounded structured status/diagnostics as secondary information. Do not directly call an adapter from React/Server Action UI code.

### R6 — Save uses the existing CAS draft lifecycle

Save an existing Policy Operation DRAFT only through the canonical `updateToolDraft`/Commerce lifecycle operation with:

```text
toolRevisionId = currently selected DRAFT id
expectedEditVersion = loaded/current CAS editVersion
definition = exact current candidate
```

Use the existing structured operation/audit reason convention.

Save must not:

```text
create a new Tool identity
change operation
change operationVersion
publish the revision
create a release
create a conversation grant
```

### R7 — Save requires the canonical current Test checkpoint

Apply the accepted provider Save/Test gate consistently:

```text
all owned authored sections current VALID
AND
current candidate Test status == PASSED for the exact current snapshot
```

A stale/failed/not-run Test prevents Save and shows an actionable Test-owned message.

Do not invent a weaker Policy Operation Save rule.

### R8 — CAS conflict and unknown outcome preserve user work

On a stale edit-version conflict or unknown mutation outcome:

```text
do not silently replace local candidate
show the existing explicit conflict/refresh recovery path
operation/version remain fixed
no implicit retry that may overwrite another editor
```

Follow the accepted persisted-DRAFT CAS semantics; do not create Policy-specific reconciliation behaviour.

### R9 — remount/return round-trip is exact

After a successful Save and subsequent remount/reselection of the DRAFT, restore exactly:

```text
description
definitionVersion
inputSchema
operation
operationVersion
argument mappings
responseTemplate
editVersion returned by Save
```

No field may fall back to a Shopify/External default simply because the editor remounted.

Opening an existing persisted Policy Operation revision performs no write.

## Work Items

- [x] Connect Policy Operation local editor state to the common persisted authoring session.
- [x] Add deterministic section validation/freshness propagation.
- [x] Integrate one Policy Operation Test tab with COMMERCE-098 and common Test state.
- [x] Gate Save on current validation plus current successful Test.
- [x] Save through canonical CAS `updateToolDraft` without changing operation/version.
- [x] Preserve local work on CAS conflict/unknown outcome using the existing recovery model.
- [x] Add exact save/remount/round-trip regressions.
- [x] Add no-write-on-open and no-rebind regressions.

## Interfaces / Contracts

Consumes:

- COMMERCE-097 Policy Operation authoring UI;
- COMMERCE-098 live-Test action;
- canonical persisted authoring-session/Test state;
- canonical Tool DRAFT CAS lifecycle.

Produces no new cross-service contract.

## Dependencies

- `ARCH-021-COMMERCE-097`
- `ARCH-021-COMMERCE-098`

## Enables

- `ARCH-021-COMMERCE-100`

## Acceptance Criteria

- [x] Existing `POLICY_OPERATION` DRAFT opens with exact persisted operation/version and no write.
- [x] All editable Policy Operation fields participate in the common validation/Test freshness model.
- [x] Operation/version cannot be rebound in Studio.
- [x] Test executes the exact current candidate through COMMERCE-098.
- [x] Editing after Test makes the checkpoint stale.
- [x] Save is blocked until all owned sections are current-valid and the exact current candidate has a PASSED Test.
- [x] Save uses the canonical DRAFT CAS operation and preserves operation/version.
- [x] CAS conflict/unknown outcome does not silently overwrite local work.
- [x] Successful Save/remount restores the exact saved Policy Operation candidate and returned editVersion.
- [x] No new Tool identity, publication, release or grant is created by Save.
- [x] Existing External HTTP and Shopify Admin Save/Test flows are unchanged.

## Validation

- [x] Focused persisted Policy Operation editor/round-trip tests.
- [x] Focused Test freshness/stale-after-edit tests.
- [x] Focused CAS conflict/unknown-outcome tests.
- [x] Focused no-rebind/no-write-on-open tests.
- [x] Existing provider regression packet required by the current Tool editor.
- [x] Targeted TypeScript diagnostics for changed files.
- [x] Targeted ESLint for changed files.
- [x] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin COMMERCE-100.

## Implementation Notes

The fixed operation binding is intentional. Studio is authoring a revision of a Tool that invokes Moda-owned code; Studio is not a backend function IDE and does not own operation registration.

## Completion Report

### Status

Ready for Architect Review (Attempt 1).

### Files Changed

- `src/studio/tools/new-tool-authoring-state.ts`
- `src/studio/tools/policy-operation-editor.tsx`
- `src/studio/tools/authoring/policy-operation-test-tab.tsx`
- `src/studio/tools/tool-editor.tsx`
- `tests/new-tool-authoring-state.test.ts`
- `tests/shopify-admin-tools-ui.test.tsx`

### Work Completed

- Extended the canonical authoring validation ledger with per-section current-valid markers; advancing a section revision clears its marker. Added focused shared-state coverage for validity and invalidation.
- Connected persisted Policy Operation editing to the common authored-section and Test snapshot lifecycle. The editor tracks Tool Definition, Request, descriptor-backed Response, and Result Template validity; current candidate edits stale Test and Save remains gated on all four current validations plus a passed Test.
- Added a single Policy Test tab that calls the authenticated C098 server action with exactly `{ definition, arguments, shopId }`. It enforces the selected shop and bounded JSON-object arguments, renders agent-facing text first, and presents bounded stage/result diagnostics second.
- Kept candidate assembly in the parent editor and preserved the loaded immutable name and operation/version binding. Save uses `updateToolDraft` with the selected revision ID, current CAS editVersion, exact candidate, and structured audit reason; successful results are identity-checked and the returned definition/editVersion restore the editor state.
- Preserved local edits on CAS conflict and exercised the real `ToolAuthoringScreen` unknown-outcome lock/recovery state after a thrown mutation. Existing open/no-write, fixed-binding, no-create/no-publish assertions remain covered.
- Left External HTTP and Shopify Admin behavior unchanged; their existing provider UI regressions pass.

### Validation Results

- Focused regression packet: 8 files passed, 174 tests passed (`new-tool-authoring-state`, persisted Shopify Admin/Policy UI, External HTTP UI, Policy live-Test service/action/authoring action, and shared authoring validation/server-action suites).
- Targeted ESLint over all six changed implementation/test files: passed without warnings.
- `git diff --check`: passed.
- `prisma generate --schema database/prisma/schema.prisma`: passed; generated output remains under ignored `node_modules` and no schema/submodule pointer changed.
- `tsc --noEmit --pretty false`: package-wide check remains non-green with 38 diagnostics in unrelated existing source/tests after Prisma Client generation; no diagnostic targets any C099-changed file. The C099 TypeScript diagnostics are clear; the repository-wide check is not claimed as passing.

### Deviations

None. The shared validity marker was added to the existing authoring ledger rather than introducing Policy-specific validation/Test state.

### Assumptions

The existing C098 authenticated Test action and canonical `updateToolDraft` lifecycle are the authoritative execution and persistence boundaries. The selected draft's loaded operation/version binding remains fixed for the editor session.

### Unresolved Issues

The package-wide TypeScript check retains 38 diagnostics outside the six changed files, primarily unrelated Commerce source and tests. They are recorded for Architect review and were not changed as out-of-scope work.

### Architectural Concerns

None identified. The implementation reuses the common persisted authoring ledger/Test model and existing CAS lifecycle; it adds no cross-service contract or provider-specific reconciliation path.

### Prepared Execution Evidence

- Launcher returned `prepared_execution: true`, `execution_state: claimed`, dependency gate passed for COMMERCE-097/098, Attempt 1, and claim commit `4beb41df2840c0bfd80f4243a69f937f9735e1f7` pushed.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-099`, `task/ARCH-021-COMMERCE-099`; prepared parent head `144643a3a8dad3390f2b93664f29687867bd4deb`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-099`, `task/ARCH-021-COMMERCE-099`; prepared implementation head `6c9326b5ee8ca2ee817b29009c86cc26a1e009f1`.
- Recursive `database` submodule is ready at `e9fb60221f1532205650154dfff2aadb6270b14c`.
- Implementation commit: `d7bd1990694e5b2a4a6c8c3c3f7b9b734aaceff6` (`feat(ARCH-021-COMMERCE-099): integrate persisted policy draft lifecycle`), pushed to `origin/task/ARCH-021-COMMERCE-099` and verified equal to the remote head. Initial parent completion-report commit `0e766f50cbc246548a89f0773e3e846b2036162f` was pushed to `origin/task/ARCH-021-COMMERCE-099`; this final report correction is also being published to that mirrored ref. No main merge, unrelated task, submodule pointer, or Architect Review section is changed.

### Submission Evidence

Return control to `moda_architect` for review. Stop before COMMERCE-100.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 is architecturally sound in its persisted Policy Operation candidate assembly, fixed operation/version binding, section validation, C098 invocation, CAS Save and conflict/unknown-outcome preservation. One live-Test freshness defect remains.

`src/studio/tools/authoring/policy-operation-test-tab.tsx` identifies a Test run by the current authored-section snapshot plus `argumentsText` and `shopId`, but it does not carry the monotonic transient-generation guard already used by the accepted Shopify Admin Test surface.

This leaves an A -> B -> A reversion race:

1. start Policy Operation Test with transient state A;
2. change Test arguments or selected shop to B, which correctly clears the visible result and marks the checkpoint stale;
3. return to A before the original A request completes;
4. because the derived identity is again byte-for-byte A and `sequence.current` has not changed, the old A result passes the current completion guards;
5. `completeAuthoringTest` sees the unchanged authored-section snapshot and can mark the checkpoint `PASSED` again, resurrecting a result that was already invalidated.

That can incorrectly re-enable Save without a new explicit Test after transient state changed.

The accepted Shopify Admin Test implementation prevents exactly this class of A -> B -> A resurrection with a monotonic provider-local transient generation. C099 should reuse that existing pattern rather than create Policy-specific semantics.

### Reviewed Files

- `src/studio/tools/new-tool-authoring-state.ts`
- `src/studio/tools/policy-operation-editor.tsx`
- `src/studio/tools/authoring/policy-operation-test-tab.tsx`
- `src/studio/tools/tool-editor.tsx`
- `src/studio/tools/authoring/shopify-admin-test-tab.tsx` as the accepted freshness reference
- `tests/new-tool-authoring-state.test.ts`
- `tests/shopify-admin-tools-ui.test.tsx`
- `docs/decisions/commerce/ARCH-021/COMMERCE-099-round-trip-and-save-policy-operation-tool-drafts.md`

### Validation Reviewed

- Submitted focused packet: 174 tests across eight files passed.
- Targeted ESLint: passed.
- `git diff --check`: passed.
- Package-wide TypeScript remains non-green with 38 diagnostics outside C099 changed files; no submitted C099 file is implicated.
- Static review confirms the fixed persisted operation/version checks and CAS `updateToolDraft` boundary are present.
- Static comparison with the accepted Shopify Admin Test tab exposes the missing monotonic transient-generation completion guard described above.

### Architecture Conformance

Changes Requested.

The implementation conforms to C097/C098 and the common persisted authoring lifecycle except for Test freshness across transient Test-input/shop reversion. The correction remains entirely within C099 scope and does not require a new task or any Save/CAS redesign.

### Follow-up

Return ARCH-021-COMMERCE-099 through the same task for Attempt 2.

Required bounded correction:

1. In `src/studio/tools/authoring/policy-operation-test-tab.tsx`, reuse the accepted Shopify Admin transient-generation pattern:
   - keep a monotonic `transientGeneration` plus ref;
   - increment it whenever the transient `{argumentsText, shopId}` identity changes;
   - include the generation in the submission identity;
   - capture `submittedGeneration` when a run starts;
   - require the current generation to equal `submittedGeneration` before accepting either successful or failed completion.
2. Preserve the existing behavior that changing arguments/shop clears transient output and stales the common Test checkpoint.
3. Add a focused regression with a deferred C098 action proving A -> B -> A reversion cannot resurrect the original A result or set the common checkpoint back to `PASSED`; Save must remain disabled until a new explicit Test completes for the current transient state.
4. Cover both Test-argument and selected-shop reversion if the existing test harness can do so without broadening scope; at minimum prove the shared monotonic mechanism with one reversion regression and retain direct coverage that both arguments and shop participate in the transient identity.
5. Do not change Policy Operation candidate assembly, fixed operation/version binding, CAS Save, conflict/unknown-outcome recovery, External HTTP, Shopify Admin semantics, or COMMERCE-100.

Re-run the focused C099 packet, targeted ESLint/changed-file diagnostics and `git diff --check`. Record package-wide TypeScript baseline only as evidence; do not repair unrelated diagnostics. Return the task to `review` and STOP before COMMERCE-100.
