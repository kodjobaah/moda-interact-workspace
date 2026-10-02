---
id: ARCH-021-COMMERCE-083
architecture_id: ARCH-021
title: Integrate Shopify Admin Test and show the populated Result Template
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 75
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-078
  - ARCH-021-COMMERCE-079
  - ARCH-021-COMMERCE-081
  - ARCH-021-COMMERCE-082
  - ARCH-021-COMMERCE-085
  - ARCH-021-COMMERCE-087
enables:
  - ARCH-021-SYSTEM-TEST-002
created: 2026-09-28
updated: 2026-09-29
---

# Integrate Shopify Admin Test and show the populated Result Template

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Integrate the already-accepted COMMERCE-082 Shopify Admin live-Test backend into the existing new-Tool and persisted-DRAFT authoring flow, display the server-rendered populated Result Template as the primary Test result, and require a current successful Shopify Test before Shopify Create/Save may persist the current candidate.

This is a UI/session integration task. It does not own Shopify Admin Test backend execution.

## Context

The required foundations are already accepted:

```text
COMMERCE-078
  common new-Tool validation/Test checkpoint

COMMERCE-079
  persisted-DRAFT authoring/CAS/dirty-state model

COMMERCE-081
  accepted provider-aware Test integration/stale-result/Save-gating pattern

COMMERCE-082
  accepted non-durable Shopify Admin live-Test backend + Server Action

COMMERCE-085 / COMMERCE-087
  final Nunjucks authoring/runtime and optional-result safety
```

C083 should apply the already-accepted External Test integration pattern to Shopify Admin without creating another execution service, Test-readiness authority, renderer or persistence mechanism.

### Attempt 1 blocker (resolved before Attempt 2)

Attempt 1 verified that its prepared C083 implementation worktree did **not** physically contain the accepted C082 Shopify Admin live-Test implementation. Before Attempt 2, the accepted C082 integration was merged into the Commerce base at `f090ccf` and verified in the prepared Attempt 2 implementation worktree.

Present:

```text
production AdminQueryExecutionPort
production Admin query execution
```

Missing:

```text
Shopify Admin live-Test domain service
ADMIN-authorized Shopify Admin live-Test Server Action
C082 live-Test input/result/stage contract
CommerceBackend exposure required by that accepted Test service
```

C083 MUST NOT recreate those capabilities. Attempt 2 consumed the accepted C082 service and action without duplicating them.

The Attempt 1 blocker is resolved; the task completed its bounded UI/session integration in Attempt 2.

## Scope

With C082 integrated, C083 changes only the Shopify Admin authoring integration surfaces needed to consume C082:

```text
src/studio/tools/new-tool-editor.tsx
src/studio/tools/tool-editor.tsx
src/studio/tools/authoring/shopify-admin-test-tab.tsx
existing C082 Shopify Admin live-Test Server Action import/call site
focused Shopify authoring/Test regressions
```

Use one reusable `ShopifyAdminTestTab` (or mechanically equivalent shared component) for:

```text
new Shopify Admin Tool
persisted Shopify Admin DRAFT
```

## Out of Scope

- Reimplementing, copying or substituting for COMMERCE-082.
- Creating another Shopify Admin Test Server Action, GraphQL transport or result contract.
- Changing C082 backend execution semantics.
- Creating another authoritative Test/pass/freshness store.
- Changing C078/C079 revision/Test semantics.
- Changing C079 CAS/persistence-dirty behavior.
- Changing C081 External Test behavior.
- Changing C084/C085/C087 Result Template grammar/editor/rendering semantics.
- Publication-proof or `LIVE_TEST_REQUIRED` changes.
- Automatic persistence after Test.
- Request/Response authoring redesign.
- React-side Result Template rendering.
- Database or cross-repository changes.

## Requirements

### R1 — integration precondition

Before source changes, verify the prepared implementation worktree physically contains the accepted C082 capabilities.

If they are absent:

```text
status = blocked
record exact missing capability
make no implementation changes
return to moda_architect
STOP
```

Do not reconstruct C082 from task documentation.

### R2 — reuse the existing common Test checkpoint

Use the accepted C078/C079 operations equivalent to:

```text
currentAuthoringSnapshot(...)
startAuthoringTest(...)
completeAuthoringTest(...)
isCurrentTestPassed(...)
```

Do not create Shopify-specific authoritative:

```text
testPassed
validated
dirty
testedSnapshot
```

Provider-specific safe display state may remain local to `ShopifyAdminTestTab`.

### R3 — submit the exact current Shopify candidate

Immediately before Test, use the same assembled definition that Review/Create/Save would persist.

Send to the existing C082 action only:

```ts
{
  definition: CommerceToolDefinition;
  arguments: Record<string, unknown>;
  shopId: string;
}
```

The browser must never provide:

```text
Shopify domain
access token
offline-session credential
Authorization header
```

### R4 — prerequisites and Test lifecycle

Do not call C082 unless all four authored sections are current VALID:

```text
Tool Definition
Request
Response
Result Template
```

Also require:

```text
selected shop
valid JSON-object Test arguments
arguments payload <= 64 KiB
complete Shopify definition parses canonically
```

On Test start:

```text
capture currentAuthoringSnapshot
capture provider-local transient generation / run identity
mark common Test RUNNING
call C082 exactly once
```

A result may mark the common Test `PASSED` only when:

```text
C082 result.kind == ok
candidateValidation == passed
shopResolution == passed
providerRequest == passed
resultValidation == passed
resultRendering == passed
renderedText is present
submitted snapshot is still current
provider-local transient generation is still current
```

A current backend/stage failure marks `FAILED`.

Any authored-section, Test-arguments or selected-shop change during the run makes that completion stale.

Use the same monotonic transient-generation principle accepted in C081 so:

```text
arguments A -> B -> A
shop A -> B -> A
```

cannot resurrect an old in-flight or displayed result.

Test-argument/shop changes are transient and must not make a persisted DRAFT persistence-dirty.

### R5 — presentation

On success, display first:

```text
Result shown to agent
<exact C082 renderedText>
```

React must not parse or rerender Nunjucks.

Safe secondary diagnostics may show only the bounded C082 stages/normalized values:

```text
candidateValidation
shopResolution
providerRequest
resultValidation
resultRendering
processedResult / normalized values
```

Do not expose credentials or unbounded provider payloads.

### R6 — Shopify Create/Save gate

For a new Shopify Tool:

```text
existing C078 Create eligibility
AND isCurrentTestPassed(session)
```

For a persisted Shopify DRAFT:

```text
existing C079 Save eligibility
AND isCurrentTestPassed(session)
```

Preserve the C081 External Test gate unchanged.

Review remains navigable when Test is NOT_RUN/RUNNING/FAILED/STALE.

### R7 — Test is non-durable

Running Test, changing Test arguments/shop, viewing results or changing Test state performs zero:

```text
createToolWithInitialDraft
updateToolDraft
Tool / ToolRevision write
audit write
operation receipt
publication-proof write
```

A successful authoring Test does not satisfy `LIVE_TEST_REQUIRED` publication proof.

### R8 — preserve existing authoring flows

Do not regress:

```text
Explore Shopify round-trip
Request validation/mapping
Response derivation
Nunjucks Result Template validation
Review derived Agent Contract
new Tool atomic Create
persisted one-CAS Save
Cancel semantics
External Test behavior
```

## Work Items

- [x] Verify accepted C082 implementation is physically present before source work.
- [x] Add one reusable Shopify Admin Test surface for new and persisted authoring.
- [x] Reuse the C078/C079 common Test checkpoint and C081 transient-generation pattern.
- [x] Submit the exact current assembled Shopify candidate to C082.
- [x] Gate Test on current authored-section validity, shop and Test-argument validity.
- [x] Display exact server `renderedText` first and bounded safe diagnostics second.
- [x] Require current Shopify Test PASS for new Create.
- [x] Require current Shopify Test PASS for persisted Save without changing C079 CAS/dirty semantics.
- [x] Preserve External C081 behavior.
- [x] Prove Test is zero-write and does not create publication proof.
- [x] Add focused new/persisted/stale/concurrency regressions.

## Interfaces / Contracts

Consumes only accepted existing boundaries:

```text
C078/C079
  common authoring Test checkpoint
  assembled current candidate
  Create/Save eligibility

C081
  monotonic provider-local transient generation pattern
  preserved External gate

C082
  Shopify Admin live-Test Server Action
  input/result/stage contract
  server renderedText
```

No new persistent, database, queue, Shared or cross-repository contract.

## Dependencies

- ARCH-021-COMMERCE-078
- ARCH-021-COMMERCE-079
- ARCH-021-COMMERCE-081
- ARCH-021-COMMERCE-082
- ARCH-021-COMMERCE-085
- ARCH-021-COMMERCE-087

## Enables

- ARCH-021-SYSTEM-TEST-002

## Acceptance Criteria

- [x] C083 blocks rather than recreates C082 if the accepted backend/action is absent.
- [x] Exactly one reusable Shopify Admin Test surface serves new and persisted authoring.
- [x] No second authoritative Shopify Test/pass/freshness state exists.
- [x] C082 receives the exact current assembled definition, arguments and selected-shop ID.
- [x] Browser supplies no Shopify domain/token/credential.
- [x] Test cannot call C082 while any authored section is stale/invalid.
- [x] Test start drives the existing common RUNNING checkpoint.
- [x] Only a fully passed current C082 result can mark Test PASSED.
- [x] Current backend/stage failure marks FAILED.
- [x] Authored-section/Test-context mutation makes late responses stale.
- [x] Argument/shop A -> B -> A cannot resurrect an old result.
- [x] `Result shown to agent` displays exact server `renderedText` first.
- [x] New Shopify Create requires current PASS.
- [x] Persisted Shopify Save requires current PASS and preserves C079 CAS/dirty semantics.
- [x] External C081 Test/Save behavior is unchanged.
- [x] Test performs no durable or publication-proof write.
- [x] Existing Explore/Request/Response/Result Template/Review/Cancel behavior remains intact.

## Validation

After C082 is physically integrated, run:

```text
npx vitest run   tests/shopify-admin-tools-ui.test.tsx   tests/tool-authoring-screen.test.tsx   tests/shopify-admin-live-test-action.test.ts
```

Add/retain focused regressions for:

```text
new Tool NOT_RUN -> Create disabled
new Tool current PASS -> Create enabled when other gates pass
persisted DRAFT NOT_RUN -> Save disabled
persisted DRAFT current PASS -> Save enabled when other gates pass
authored edit after PASS -> STALE
Test arguments/shop change -> STALE without persistence-dirty
arguments A -> B -> A stale-result protection
shop A -> B -> A stale-result protection
run N cannot overwrite run N+1
failed C082 stage -> FAILED, never PASSED
missing shop -> zero action call
successful renderedText shown first
browser request contains no credential/domain fields
zero create/save/publication mutation during Test
existing External C081 regressions remain green
```

Also run:

```text
targeted ESLint for changed files
changed-file TypeScript diagnostics
git diff --check
```

## Stop Condition

While C082 is absent, remain Blocked and STOP.

After the blocker is resolved and the defined implementation/validation is complete:

```text
finish Completion Report
set status review
clear execution claim
return to moda_architect
STOP
```

Do not begin SYSTEM-TEST-002.

## Implementation Notes

C082 is the sole Shopify Admin Test execution authority.

C083 is intentionally an integration task:

```text
existing authoring candidate
        +
existing common Test checkpoint
        +
existing C082 backend
        ->
Shopify Test UI
        ->
current PASS gate for Create/Save
```

Keep provider execution and Result Template rendering on the server.

## Completion Report


### Status

Blocked: accepted COMMERCE-082 Shopify Admin live-Test implementation is not integrated into the C083 implementation worktree.

### Files Changed

None. Per R1, no C082 capability was recreated and no application source was changed.

### Work Completed

- Verified the prepared `moda-interact-commerce` implementation worktree for the C082 capabilities required by R1.
- The required `src/commerce/tool-authoring/shopify-admin-live-test.ts` domain service and `src/studio/tools/shopify-admin-live-test-server-actions.ts` action are absent.
- Bounded file and symbol searches found no alternate Shopify Admin live-Test service/action, ShopifyAdmin live-Test input/result types, candidate/shop/provider/result stage contract, or ADMIN-authorized Test Server Action.
- The existing production `AdminQueryExecutionPort` and `src/commerce/query/admin.ts` are present, but do not provide the accepted non-durable C082 live-Test capability and cannot substitute for it.
- Followed R1: did not implement, copy, or create a substitute for C082; stopped before C083 integration work.

### Validation Results

- Launcher preparation passed for Attempt 1: dependency gate passed; dependencies ARCH-021-COMMERCE-078, -079, -081, -082, -085 and -087 were reported complete; implementation worktree and recursive submodule were prepared.
- R1 capability checks in the prepared implementation worktree: exact expected domain-service and Server Action paths absent; alternate `*shopify*test*` and `*live*test*` source file searches returned no matches; bounded symbol searches found only the existing External live-Test service and production Admin query port, not C082 live-Test capabilities.
- No application tests, lint, or TypeScript validation were run because R1 requires stopping before implementation when C082 is absent.

### Deviations

Implementation and downstream C083 validation were not started, as required by R1's stop condition.

### Assumptions

The parent task metadata says COMMERCE-082 is complete, but the prepared implementation branch is the authority for whether its accepted source is physically integrated for C083. The observed source gap requires developer integration/update to the accepted C082 implementation before this task can proceed.

### Unresolved Issues

Missing integrated COMMERCE-082 Shopify Admin live-Test implementation. Required capabilities include the Shopify Admin live-Test domain service, ADMIN-authorized Server Action, input/result types and staged result contract, plus exposure of the Admin execution port to that action. `moda_architect` must coordinate integration of the accepted C082 implementation, then return C083 to ready for a new attempt.

### Architectural Concerns

Proceeding by recreating C082 inside C083 would violate R1 and risk duplicating the accepted backend/action contract. No such implementation was attempted.

### Git / VCS

- Canonical task file: `docs/decisions/commerce/ARCH-021/COMMERCE-083-integrate-shopify-admin-test-tab.md`
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-083`
- Parent branch: `task/ARCH-021-COMMERCE-083`
- Parent task branch claim was already committed and pushed by the launcher; no additional claim was created.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-083`
- Implementation branch: `task/ARCH-021-COMMERCE-083`; no implementation files changed and no implementation commit created.
- Parent submodule gitlink staged: no.
- Merged to implementation main: no.
- Merged to workspace main: no.

### Attempt 2 Completion Report

#### Status

Implemented and validated. Returned to `moda_architect` for review.

#### Files Changed

- `src/studio/tools/authoring/shopify-admin-test-tab.tsx` — shared transient Admin Test UI for new and persisted authoring.
- `src/studio/tools/new-tool-editor.tsx` — integrated Test and current-PASS Create gate.
- `src/studio/tools/tool-editor.tsx` — integrated Test, current-PASS Save UI and submit guard, while preserving the External branch.
- `tests/shopify-admin-tools-ui.test.tsx`, `tests/tool-authoring-screen.test.tsx`, `tests/shopify-admin-live-test-action.test.ts` — focused UI/action and lifecycle regressions.

#### Work Completed

- Verified the accepted C082 live-Test domain service, ADMIN-authorized Server Action, stage/result contract, and Commerce backend exposure were present in the Attempt 2 base (`f090ccf`). No C082 execution capability was recreated.
- Added one shared `ShopifyAdminTestTab` using the common C078/C079 checkpoint and provider-local monotonic generation/sequence checks. It submits the assembled definition, parsed object arguments, and selected shop ID only; the UI enforces the accepted backend's 16 KiB argument limit.
- Gated Test on valid current authoring sections, shop selection, and valid arguments. The server-provided `renderedText` is shown first; only bounded stages/issues and normalized result are secondary.
- Gated new Create and persisted Save on current Test PASS, including the persisted form submit handler, without changing C079 compare-and-swap or dirty-state semantics. Successful Test remains transient and performs no Tool, revision, audit, receipt, or publication-proof write.
- Preserved External C081 behavior. A changed-file typecheck review exposed accidental Admin Review references in the External branch; those were restored to the committed C081 behavior, then both authoring UI suites and the complete task packet were rerun successfully.
- Added regressions for NOT_RUN Create/Save gating, direct persisted form-submit blocking, current-pass behavior, exact no-credential payload shape, zero-write behavior, failed C082 stages, missing shop, stale arguments, combined shop/argument A-to-B-to-A transitions, and old-run completion after a newer run.

#### Validation Results

- Required packet: `npx vitest run tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/shopify-admin-live-test-action.test.ts` — 3 files, 62 tests passed.
- Targeted ESLint on all six changed files — 0 errors, 0 warnings.
- Changed-file TypeScript diagnostics — no diagnostics in the six changed files.
- `git diff --check` — passed.
- Package-wide `npx tsc --noEmit` is not a clean project gate: its earlier run reported diagnostics in other files. No changed-file diagnostics remained after the External branch restoration.

#### Deviations and Assumptions

- The accepted C082 backend caps arguments at 16 KiB, tighter than the task's 64 KiB ceiling; the UI matches the backend limit to avoid requests that the action must reject.
- No database, Shared, queue, publication-proof, or cross-repository contract was changed.

#### Unresolved Issues

- None within C083 scope. `ARCH-021-SYSTEM-TEST-002` remains pending and was not started.

#### Git / VCS

- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-083`
- Implementation branch: `task/ARCH-021-COMMERCE-083`
- Implementation commit: `d15d2ab` (`feat(commerce): integrate Shopify Admin authoring test`), pushed to `origin/task/ARCH-021-COMMERCE-083`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-083`
- Parent branch: `task/ARCH-021-COMMERCE-083`; this report is the only parent-worktree change for Attempt 2.
- Parent submodule gitlink staged: no. Merged to implementation main: no. Merged to workspace main: no.
- Task status set to `review`; execution claim cleared; handed back to `moda_architect`.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 is accepted.

Attempt 1 correctly blocked when the prepared implementation worktree did not physically contain the accepted COMMERCE-082 Shopify Admin live-Test capability. Before Attempt 2, the accepted C082 integration was brought into the Commerce base and verified at base commit `f090ccf`. C083 then consumed that implementation without recreating or substituting for C082.

The refined C083 integration contract is satisfied:

- exactly one reusable `ShopifyAdminTestTab` serves new Shopify Admin Tools and persisted Shopify Admin DRAFTs;
- C082 remains the sole Shopify Admin live-Test backend / Server Action authority;
- the exact assembled current Shopify definition, parsed Test arguments and selected `shopId` are submitted;
- browser input contains no Shopify domain, access token, offline-session credential or Authorization header;
- Test is locally gated on current Tool Definition, Request, Response and Result Template readiness plus selected shop and bounded JSON-object arguments;
- the accepted C078/C079 common Test checkpoint is reused rather than replaced by Shopify-specific authoritative state;
- provider-local transient state uses a monotonic generation / run sequence so argument or shop A -> B -> A reversion cannot resurrect an old in-flight or displayed result;
- only a current C082 result with all required stages passed and server `renderedText` present may satisfy the common PASS checkpoint;
- current backend/stage failure produces FAILED; authored/Test-context mutation makes late completion stale;
- server-returned `renderedText` is displayed first under `Result shown to agent`; React does not render Nunjucks;
- safe bounded C082 stages/issues/normalized result remain secondary;
- new Shopify Create requires the existing C078 gates plus a current PASS;
- persisted Shopify Save requires the existing C079 gates plus a current PASS, including the direct form-submit handler;
- Test-argument/shop changes remain transient and do not change persisted-DRAFT dirtiness;
- running Test performs no Tool, ToolRevision, audit, operation-receipt or publication-proof write;
- successful authoring Test remains separate from the existing publication `LIVE_TEST_REQUIRED` proof; and
- accepted External C081 behavior remains intact.

The UI's 16 KiB Test-argument limit is intentionally stricter than C083's original 64 KiB ceiling because the accepted C082 backend contract itself enforces 16 KiB. Matching the server authority is the correct integration behavior and does not require a C082 contract change.

### Reviewed Files

- `src/studio/tools/authoring/shopify-admin-test-tab.tsx`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/tool-editor.tsx`
- `src/studio/tools/shopify-admin-live-test-server-actions.ts`
- `src/commerce/tool-authoring/shopify-admin-live-test.ts`
- `tests/shopify-admin-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`
- `tests/shopify-admin-live-test-action.test.ts`
- C083 Completion Report — Attempts 1 and 2
- COMMERCE-088 dependency/task record
- ARCH-021 SYSTEM-TEST-002 dependency record

### Validation Reviewed

Attempt 2 submitted evidence:

- required C083 packet: **3 files, 62 tests passed**;
- targeted ESLint for the six changed implementation/test files: passed;
- changed-file TypeScript diagnostics: clean;
- `git diff --check`: passed;
- implementation commit `d15d2ab` pushed to `origin/task/ARCH-021-COMMERCE-083`;
- parent report commit `a39a6736` pushed;
- parent and implementation worktrees reported clean and synchronized.

The earlier package-wide TypeScript run was non-green across unrelated files. No changed-file diagnostics remain, so that broader state is not a C083 blocker.

Direct source/test inspection confirms the common checkpoint, transient-generation stale-result protection, exact action payload, current-PASS persistence gates, submit-handler guard, zero-write Test behavior and External preservation.

### Architecture Conformance

Conforms.

C083 is now the intended thin Studio integration layer over accepted C082 execution. It does not duplicate provider execution, rendering, Test contracts, authoring checkpoint semantics or persistence behavior.

### Follow-up

C083 is Complete / Accepted — Attempt 2.

COMMERCE-088 becomes Ready because C078 and C083 are Complete.

ARCH-021-SYSTEM-TEST-002 remains Pending because it also depends on COMMERCE-088. Do not start the system-test task until C088 is architect-accepted Complete.
