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
status: ready
priority: 75
executor: null
claimed_at: null
attempt: 1
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

### Current blocker

Attempt 1 verified that the prepared C083 implementation worktree does **not** physically contain the accepted C082 Shopify Admin live-Test implementation.

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

C083 MUST NOT recreate those capabilities.

The accepted C082 implementation (previously reviewed from implementation commit `c4876fa`, or a later integrated commit containing the same accepted capability) must first be integrated into the Commerce implementation base used by C083.

After that integration is present, `moda_architect` returns this same task from `blocked` to `ready`; the next execution claim becomes Attempt 2.

## Scope

After the blocker is resolved, C083 may change only the Shopify Admin authoring integration surfaces needed to consume C082:

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

- [ ] Verify accepted C082 implementation is physically present before source work.
- [ ] Add one reusable Shopify Admin Test surface for new and persisted authoring.
- [ ] Reuse the C078/C079 common Test checkpoint and C081 transient-generation pattern.
- [ ] Submit the exact current assembled Shopify candidate to C082.
- [ ] Gate Test on current authored-section validity, shop and Test-argument validity.
- [ ] Display exact server `renderedText` first and bounded safe diagnostics second.
- [ ] Require current Shopify Test PASS for new Create.
- [ ] Require current Shopify Test PASS for persisted Save without changing C079 CAS/dirty semantics.
- [ ] Preserve External C081 behavior.
- [ ] Prove Test is zero-write and does not create publication proof.
- [ ] Add focused new/persisted/stale/concurrency regressions.

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

- [ ] C083 blocks rather than recreates C082 if the accepted backend/action is absent.
- [ ] Exactly one reusable Shopify Admin Test surface serves new and persisted authoring.
- [ ] No second authoritative Shopify Test/pass/freshness state exists.
- [ ] C082 receives the exact current assembled definition, arguments and selected-shop ID.
- [ ] Browser supplies no Shopify domain/token/credential.
- [ ] Test cannot call C082 while any authored section is stale/invalid.
- [ ] Test start drives the existing common RUNNING checkpoint.
- [ ] Only a fully passed current C082 result can mark Test PASSED.
- [ ] Current backend/stage failure marks FAILED.
- [ ] Authored-section/Test-context mutation makes late responses stale.
- [ ] Argument/shop A -> B -> A cannot resurrect an old result.
- [ ] `Result shown to agent` displays exact server `renderedText` first.
- [ ] New Shopify Create requires current PASS.
- [ ] Persisted Shopify Save requires current PASS and preserves C079 CAS/dirty semantics.
- [ ] External C081 Test/Save behavior is unchanged.
- [ ] Test performs no durable or publication-proof write.
- [ ] Existing Explore/Request/Response/Result Template/Review/Cancel behavior remains intact.

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

## Architect Review

### Review Status

Blocked

### Review Notes

Attempt 1 correctly followed the integration precondition and stopped without implementation.

The parent architecture records COMMERCE-082 as Complete/Accepted, but the prepared C083 `moda-interact-commerce` worktree does not contain the accepted C082 Shopify Admin live-Test service, Server Action, input/result/stage contract or equivalent integrated capability. The production `AdminQueryExecutionPort` alone is not a substitute.

C083 MUST NOT recreate C082.

Unblock condition:

1. integrate the already-accepted C082 implementation into the Commerce implementation base used by new task worktrees — accepted handoff implementation commit `c4876fa` or a later commit containing the same reviewed capability;
2. verify the C082 domain service, ADMIN-authorized Server Action, result/stage types and required CommerceBackend exposure are physically present;
3. return this same C083 task from `blocked` to `ready`;
4. the next normal claim becomes Attempt 2.

The implementation worktree for Attempt 1 made no source changes, which is correct.

This review also refines C083 to the bounded UI/session integration scope above. The previous duplicated restatement of C078/C079/C081 contracts is superseded by references to those accepted owners.

### Reviewed Files

- `docs/decisions/commerce/ARCH-021/COMMERCE-083-integrate-shopify-admin-test-tab.md`
- accepted COMMERCE-082 task record / Completion Report
- prepared C083 Commerce source tree capability search evidence
- Commerce domain index
- parent ARCH-021 execution plan

### Validation Reviewed

- Attempt 1 launcher dependency gate: passed.
- Prepared implementation worktree capability check: C082 live-Test service/action absent.
- Bounded file/symbol searches: no equivalent accepted C082 staged live-Test implementation found.
- No application tests/lint/typecheck were required after the R1/precondition failure because implementation correctly stopped.

### Architecture Conformance

Blocked by integration drift, not by a C083 implementation defect.

The task correctly refused to duplicate C082. The refined scope conforms once the accepted C082 implementation is physically integrated.

### Follow-up

`moda_architect` / developer integration step: integrate the accepted C082 implementation into the Commerce base, then return C083 to Ready for Attempt 2.

SYSTEM-TEST-002 remains Pending.
