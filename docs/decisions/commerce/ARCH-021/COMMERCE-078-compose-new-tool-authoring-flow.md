---
id: ARCH-021-COMMERCE-078
architecture_id: ARCH-021
title: Compose the new Tool authoring flow and derived Review contract
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 74
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-021-COMMERCE-077
  - ARCH-021-COMMERCE-063
  - ARCH-021-COMMERCE-066
  - ARCH-021-COMMERCE-067
  - ARCH-021-COMMERCE-068
enables:
  - ARCH-021-COMMERCE-079
  - ARCH-021-COMMERCE-081
  - ARCH-021-COMMERCE-083
created: 2026-09-28
updated: 2026-09-28
---

# Compose the new Tool authoring flow and derived Review contract

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Implement the agreed new-Tool sequence exactly as **Tool Definition -> Request -> Response -> Result Template -> Test -> Review**, remove Agent Contract as an authoring tab, make Request own the agent input schema, make Result Template own `responseTemplate`, and show the derived Agent Contract read-only in Review with final **Save** and **Cancel** actions.

## Context

The current snapshot exposes `Request -> Response -> Test -> Agent contract -> Review`. `AgentContractTab` edits definition version, description, input schema and response template. `ResultTemplateTab` exists but is disconnected. Review currently prints `responseTemplate` under Agent contract.

COMMERCE-077 supplies the first-class Tool Definition session. COMMERCE-063/066/067 already supply the source-neutral result-contract/template boundary and the call-side Agent validator. This task composes those accepted capabilities into the product flow requested for Tool creation.

## Scope

Primary implementation areas:

```text
src/studio/tools/authoring/tool-authoring-tabs.tsx
src/studio/tools/authoring/tool-definition-tab.tsx
src/studio/tools/authoring/result-template-tab.tsx          # consume; change only for integration defects
src/studio/tools/authoring/review-tab.tsx
src/studio/tools/new-tool-editor.tsx
src/studio/external-http/request-tab.tsx                    # consume or host input-schema editor through wrapper
src/studio/tools/agent-contract-validation-server-actions.ts # consume canonical call-side action only
```

Tests:

```text
tests/tool-authoring-screen.test.tsx
tests/external-tools-ui.test.tsx
tests/shopify-admin-tools-ui.test.tsx
tests/result-template-tab.test.tsx
```

This task changes new-Tool composition only. Persisted-DRAFT parity is COMMERCE-079.

## Out of Scope

- Persisted-DRAFT authoring parity; COMMERCE-079.
- Changing Result Template syntax/grammar.
- External live-Test backend/rendering; COMMERCE-080/081.
- Shopify live-Test backend/UI; COMMERCE-082/083.
- Provider networking.
- Publication proof, validation-receipt or publication-gate changes.
- New database fields or cross-service contracts.
- Sequential Next/Previous navigation or validation gating beyond preventing provider-specific tabs from executing without a selected provider.

## Requirements

### R1 — exact new-Tool tab registry

For new Tool authoring the visible tabs, in exact order and labels, are:

```text
Tool Definition
Request
Response
Result Template
Test
Review
```

There is no `Agent contract` tab. There is no second provider-specific tab registry.

### R2 — Request owns the call-side input schema

For both providers, Request owns `definition.inputSchema`.

Shopify already renders `Input JSON Schema` in Request; preserve it.

External Request must render the same logical `Input JSON Schema` authoring control before/with its existing connection/request mapping editor. Invalid raw JSON remains local and visible; it does not overwrite the last valid candidate. External Request validation/preview/live-Test input must consume the latest valid/parsed Request-owned schema.

No input-schema editor may remain under Agent Contract because Agent Contract is no longer an authoring surface.

### R3 — Result Template is immediately after Response

Render the existing `ResultTemplateTab` on `result-template`.

The template edits exactly `definition.responseTemplate`; do not create a parallel response-template model.

Compile its bindings from the same runtime result envelope the renderer uses:

```text
External HTTP:
  compileToolResultContract(externalOutputSchema(execution.resultSchema))

Shopify Admin:
  createAdminCommerceCompiler().compile(execution, inputSchema).outputSchema
  (or an existing source-neutral helper that returns this exact schema)
```

This is important: templates address `result.values...` in production. Do not compile External bindings from the inner `resultSchema` alone.

Use the canonical Result Template validation action/validator owned by COMMERCE-063. A Response/result-contract change must make prior template validation stale.

### R4 — Agent Contract is derived and read-only in Review

Delete new-Tool use of `AgentContractTab` and the deprecated `validateAgentContractAction` path.

Review must contain a distinct read-only card headed exactly `Agent Contract` showing:

```text
definitionVersion
description
inputSchema
```

The card is derived from the current Tool Definition + Request state. It must not contain `responseTemplate`, Result Template validation or editable controls.

The current canonical call-side validator is `validateAgentCallContract` / `validateAgentCallContractAction`; if Review displays validation status, it must use this boundary only.

### R5 — Review separates all authored concepts

Review must present, as separate cards/sections:

```text
Tool Definition
Request
Response / Result Contract
Result Template
Agent Contract
```

Result Template must not be nested under Agent Contract.

Review content is read-only; edits happen on owning tabs.

### R6 — final new-Tool actions are Save and Cancel

For a new Tool, Review actions are exactly:

```text
Cancel
Save
```

`Save` performs the existing single atomic `createToolWithInitialDraft` through `ToolAuthoringScreen` using:

```text
name          = current Tool Definition name
displayName   = current Tool Definition displayName
description   = current Tool Definition description
proposedDefinition.name        = same name
proposedDefinition.description = same description
```

`Save` remains disabled until the complete current candidate parses through `CommerceToolDefinitionSchema`/the accepted draft validation boundary and provider-specific Response prerequisites are satisfied.

`Cancel` must clear the local authoring session, any matching Explore `sessionStorage` handoff, dirty state and transient validation/Test state, then return to the Tool library on `/tools`. It performs zero durable write.

### R7 — authoring remains browser-local before Save

Changing Tool Definition, Request, Response or Result Template and running local validation may update browser/component/sessionStorage state only. No tab change or validation checkpoint may create a Tool/ToolRevision.

### R8 — COMMERCE-076 is superseded, not layered on top

Do not restore C076's six-tab order (`Request -> Response -> Test -> Agent contract -> Result template -> Review`). The new flow replaces it. Reuse the surviving C066/C067/C068 implementation primitives but follow this task's product order/ownership.


### R9 — Test state is part of the authoring session; C078 does not reimplement Test execution

COMMERCE-080 and COMMERCE-082 already provide the canonical External HTTP and Shopify Admin non-durable live-Test backends respectively.

C078 MUST NOT:

```text
- implement another External live-Test service;
- implement another Shopify live-Test service;
- duplicate either Server Action;
- duplicate provider execution;
- duplicate Result Template rendering;
- create another Test result contract.
```

C078 establishes only the common session-level Test freshness/checkpoint model that COMMERCE-081 and COMMERCE-083 will drive.

Add exactly one Test state to the new-Tool authoring session:

```ts
type AuthoringTestStatus =
  | "NOT_RUN"
  | "RUNNING"
  | "PASSED"
  | "FAILED"
  | "STALE";

type AuthoringTestSnapshot = {
  toolDefinitionRevision: number;
  requestRevision: number;
  responseRevision: number;
  resultTemplateRevision: number;
};

type AuthoringTestState = {
  status: AuthoringTestStatus;
  testedSnapshot: AuthoringTestSnapshot | null;
};
```

Initial state is exactly:

```ts
{
  status: "NOT_RUN",
  testedSnapshot: null
}
```

Do not store provider result payloads in this common state model as part of C078. COMMERCE-081 and COMMERCE-083 may keep their provider-specific safe Test result/diagnostic state while updating this common Test checkpoint.

Define:

```ts
function currentAuthoringSnapshot(
  session: ToolAuthoringSession
): AuthoringTestSnapshot {
  return {
    toolDefinitionRevision:
      session.validation.toolDefinition.revision,
    requestRevision:
      session.validation.request.revision,
    responseRevision:
      session.validation.response.revision,
    resultTemplateRevision:
      session.validation.resultTemplate.revision,
  };
}
```

Define current successful Test exactly as:

```ts
function isCurrentTestPassed(
  session: ToolAuthoringSession
): boolean {
  if (
    session.test.status !== "PASSED" ||
    session.test.testedSnapshot === null
  ) {
    return false;
  }

  return (
    session.test.testedSnapshot.toolDefinitionRevision ===
      session.validation.toolDefinition.revision &&
    session.test.testedSnapshot.requestRevision ===
      session.validation.request.revision &&
    session.test.testedSnapshot.responseRevision ===
      session.validation.response.revision &&
    session.test.testedSnapshot.resultTemplateRevision ===
      session.validation.resultTemplate.revision
  );
}
```

C078 must expose sufficient session operations for COMMERCE-081 and COMMERCE-083 to drive the following transitions without duplicating provider execution.

On Test start, downstream integration must be able to capture the exact current snapshot and set:

```ts
test.status = "RUNNING";
```

On successful backend Test, if the current authoring snapshot still equals the submitted snapshot:

```ts
test.status = "PASSED";
test.testedSnapshot = submittedSnapshot;
```

On backend Test failure, if the snapshot still matches:

```ts
test.status = "FAILED";
test.testedSnapshot = submittedSnapshot;
```

If authoring state changed while Test was running, the returned result must not mark the current candidate PASSED:

```ts
test.status = "STALE";
test.testedSnapshot = null;
```

C078 establishes these common session semantics only.

COMMERCE-081 and COMMERCE-083 remain responsible for invoking the already-existing COMMERCE-080 / COMMERCE-082 provider Test backends, holding any provider-specific safe result/diagnostic state and applying the transitions above.

## Work Items

- [x] Replace the new-Tool tab registry with the exact six-step sequence.
- [x] Remove Agent Contract as a new-Tool authoring tab.
- [x] Move/retain all input-schema authoring under Request for both providers.
- [x] Wire `ResultTemplateTab` immediately after Response using production-envelope result contracts.
- [x] Use canonical Result Template validation and stale-state semantics.
- [x] Build a read-only derived Agent Contract Review card.
- [x] Separate Tool Definition, Request, Result Contract, Result Template and Agent Contract in Review.
- [x] Change new-Tool Review actions to `Cancel` + `Save`.
- [x] Make Save use the single current Tool Definition identity/description plus the assembled candidate.
- [x] Make Cancel abandon all local/session handoff state without persistence.
- [x] Add exact tab-order/ownership/persistence regressions for both provider kinds.
- [ ] Add the common Test checkpoint/freshness state, exact snapshot helpers and downstream transition operations without provider execution.

## Interfaces / Contracts

Consumes only Commerce-owned contracts:

```text
ARCH-021-COMMERCE-063  ToolResultContract + Result Template validation
ARCH-021-COMMERCE-066  ResultTemplateTab
ARCH-021-COMMERCE-067  call-side Agent validation
ARCH-021-COMMERCE-068  accepted ownership separation primitives
ARCH-021-COMMERCE-077  Tool Definition/local-session model
externalOutputSchema   canonical External runtime result envelope
Admin compiler outputSchema canonical Shopify Admin runtime result envelope
```

No new persistent/cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-077
- ARCH-021-COMMERCE-063
- ARCH-021-COMMERCE-066
- ARCH-021-COMMERCE-067
- ARCH-021-COMMERCE-068

## Enables

- ARCH-021-COMMERCE-079
- ARCH-021-COMMERCE-081
- ARCH-021-COMMERCE-083

## Acceptance Criteria

- [x] New Tool authoring exposes exactly `Tool Definition -> Request -> Response -> Result Template -> Test -> Review`.
- [x] Agent Contract is absent from the tab list.
- [x] External and Shopify input schemas are authored only from Request.
- [x] Result Template is authored only from its dedicated tab and edits the canonical `responseTemplate`.
- [x] External template bindings include production `values` paths rather than inner-schema-only paths.
- [x] Shopify template bindings come from the Admin compiler output contract.
- [x] Review shows Agent Contract read-only and contains no template editor/template JSON under Agent Contract.
- [x] Review shows Result Template separately.
- [x] New Tool final buttons are `Cancel` and `Save`.
- [x] Save performs exactly one final create operation; Cancel performs none.
- [x] No edit/validation/tab navigation before Save creates durable Tool state.
- [x] Existing Shopify Explore round-trip and current Request/Response authoring remain functional.
- [ ] New-Tool authoring session contains exactly one common `test` checkpoint with initial `NOT_RUN` / `testedSnapshot: null`.
- [ ] `currentAuthoringSnapshot(session)` returns exactly the Tool Definition, Request, Response and Result Template validation revisions.
- [ ] `isCurrentTestPassed(session)` returns true only for `PASSED` with an exact current snapshot match.
- [ ] Session operations support RUNNING, PASSED, FAILED and STALE transitions without storing provider payloads in the common Test state.
- [ ] A stale completion clears `testedSnapshot` and cannot make the current candidate PASSED.
- [ ] C078 does not call, duplicate or replace the COMMERCE-080 / COMMERCE-082 live-Test backends, Server Actions, provider execution, Result Template rendering or result contracts.

## Validation

- [x] `npx vitest run tests/tool-authoring-screen.test.tsx tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/result-template-tab.test.tsx`
- [x] focused assertions for exact tab order and absence of Agent Contract tab
- [x] focused assertions for Request-owned input schema for External + Shopify
- [x] focused assertions for production-envelope Result Template bindings
- [x] focused Save-once / Cancel-zero-write tests
- [x] targeted ESLint for changed files
- [x] changed-file TypeScript diagnostics, or repository typecheck with baseline reconciliation
- [x] `git diff --check`
- [ ] focused unit regressions for initial Test state, exact snapshot creation, exact-current PASSED semantics and stale mismatch semantics
- [ ] focused regression proving C078 common Test-state operations do not invoke provider Test services/Server Actions

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not begin an enabled or adjacent task.

## Implementation Notes

Do not delete `AgentContractTab` solely because new Tool authoring no longer uses it; persisted/legacy consumers are handled by COMMERCE-079. It may become removable only when that follow-up proves no supported consumer remains.

The flow is ordered for comprehension, not as a full wizard gate. After provider selection, existing free tab navigation may remain unless a tab cannot safely render without required local provider state.

## Completion Report

### Status

Attempt 3 complete; resubmitted for Architect Review.

### Execution Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent task worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-078`, `task/ARCH-021-COMMERCE-078`
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-078`, `task/ARCH-021-COMMERCE-078`
- Shared workspace and implementation reference checkouts were not switched or modified; no other task worktree was reused.
- Parent task remote branch fast-forwarded: not-needed; `origin/main` incorporated: already-current.
- Implementation remote task branch fast-forwarded: not-needed; `origin/main` incorporated: yes.
- Recursive submodule sync and initialization passed; `database` is initialized at `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.

### Files Changed

- `src/studio/tools/authoring/result-template-contract-adapter.ts`
- `src/studio/tools/authoring/result-template-tab.tsx`
- `src/studio/tools/authoring/review-tab.tsx`
- `src/studio/tools/authoring/tool-authoring-tabs.tsx`
- `src/studio/external-http/editor.tsx`
- `src/studio/tools/new-tool-authoring-state.ts`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/tool-authoring-screen.tsx`
- `tests/external-tools-ui.test.tsx`
- `tests/shopify-admin-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`

### Work Completed

- Composed the six required new-Tool tabs, moved input-schema authoring to Request, and retained the legacy Agent Contract tab for existing consumers.
- Connected Result Template authoring to canonical `responseTemplate` validation and provider production output envelopes, including Shopify Admin compiler output.
- Added read-only, separately grouped Review sections and Save/Cancel actions; Save uses the single atomic create path and Cancel clears local/session state without writing.
- Added provider, tab-order, Save-once, Cancel-zero-write, and no-premature-persistence regressions.
- Attempt 2 correction: split new-Tool and persisted-DRAFT tab registries so persisted External and Shopify flows retain `Request -> Response -> Test -> Agent contract -> Review` until C079; focused tests assert both orders and preserve Agent Contract editing without persistence.
- Attempt 2 correction: moved the External Request Input JSON Schema control ahead of the connection/request mapping editor; a DOM-order regression verifies it precedes Connection while invalid local input creates no durable Tool state.
- Attempt 3 correction: downstream tabs are shown whenever a provider is committed, independently of MCP name, display name, description, or overall definition validity; an unselected session shows only Tool Definition with provider-selection guidance.
- Attempt 3 correction: provider-switch confirmation keeps the original provider and tabs until confirmed; Cancel preserves it, while reset commits the new provider and retains the six-tab navigation.
- Attempt 3 correction: opening a blank local session no longer marks it dirty; provider selection or another authoring mutation still activates discard protection.
- Added focused regressions for pristine Back/no write, blank-identity selection of both providers, provider switch cancel/reset, and pristine-versus-mutated dirty navigation. Attempt 1 tab-boundary and External schema-order regressions remain in place.

### Validation Results

- Required Vitest command passed on Attempt 3: 4 files, 139 tests.
- Focused `tests/tool-authoring-screen.test.tsx` suite passed: 29 tests.
- Targeted ESLint passed for all Attempt 3 changed implementation and test files.
- Editor diagnostics reported no errors in any Attempt 3 changed C078 file.
- `git diff --check` passed.
- Full repository typecheck was not rerun on Attempt 3; Attempt 1 recorded the existing non-green repository baseline. Changed-file diagnostics are clean.

### Deviations

The full repository typecheck was not rerun on Attempt 3. Attempt 1 recorded the existing non-green repository baseline; no editor diagnostics were reported for changed C078 files.

### Assumptions

Existing Agent Contract consumers remain supported; persisted-DRAFT parity stays with COMMERCE-079.

### Unresolved Issues

No unresolved C078 implementation or validation issues. The full repository typecheck was not rerun on Attempt 3; the previously recorded baseline remains noted above.

### Architectural Concerns

None identified.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 3 satisfies the clarified navigation and pristine-session corrections from the amended Attempt 2 review.

The following Attempt 3 behaviors are accepted:

- before provider selection, the blank new-Tool session shows only `Tool Definition` plus provider-selection guidance;
- selecting Shopify Admin GraphQL or External HTTP/API reveals exactly `Tool Definition -> Request -> Response -> Result Template -> Test -> Review` without requiring the remaining Tool Definition fields to validate;
- provider-switch confirmation preserves the committed provider until reset is confirmed;
- the pristine new-Tool session starts clean, so immediate Back does not open the discard dialog;
- a real authoring mutation still enables the existing discard protection;
- persisted External/Shopify DRAFT composition remains outside C078; and
- External `Input JSON Schema` remains before the connection/request mapping controls.

The submitted 139-test packet and manual validation are sufficient for those corrections.

C078 is not accepted yet because the architecture now requires the common Test checkpoint/freshness state described in R9. This requirement is intentionally session-only and MUST NOT move provider Test execution into C078.

#### Required Attempt 4 correction — establish the common Test freshness model only

COMMERCE-080 and COMMERCE-082 already own the canonical External HTTP and Shopify Admin non-durable Test backends.

C078 MUST NOT:

```text
- implement another External live-Test service;
- implement another Shopify live-Test service;
- duplicate either Server Action;
- duplicate provider execution;
- duplicate Result Template rendering;
- create another Test result contract.
```

Implement exactly one common Test checkpoint on the new-Tool authoring session:

```ts
type AuthoringTestStatus =
  | "NOT_RUN"
  | "RUNNING"
  | "PASSED"
  | "FAILED"
  | "STALE";

type AuthoringTestSnapshot = {
  toolDefinitionRevision: number;
  requestRevision: number;
  responseRevision: number;
  resultTemplateRevision: number;
};

type AuthoringTestState = {
  status: AuthoringTestStatus;
  testedSnapshot: AuthoringTestSnapshot | null;
};
```

Initial state:

```ts
{
  status: "NOT_RUN",
  testedSnapshot: null
}
```

The common state must not contain provider response/result payloads or provider-specific diagnostics.

Define the exact snapshot helper:

```ts
function currentAuthoringSnapshot(
  session: ToolAuthoringSession
): AuthoringTestSnapshot {
  return {
    toolDefinitionRevision:
      session.validation.toolDefinition.revision,
    requestRevision:
      session.validation.request.revision,
    responseRevision:
      session.validation.response.revision,
    resultTemplateRevision:
      session.validation.resultTemplate.revision,
  };
}
```

Define the exact current-pass predicate:

```ts
function isCurrentTestPassed(
  session: ToolAuthoringSession
): boolean {
  if (
    session.test.status !== "PASSED" ||
    session.test.testedSnapshot === null
  ) {
    return false;
  }

  return (
    session.test.testedSnapshot.toolDefinitionRevision ===
      session.validation.toolDefinition.revision &&
    session.test.testedSnapshot.requestRevision ===
      session.validation.request.revision &&
    session.test.testedSnapshot.responseRevision ===
      session.validation.response.revision &&
    session.test.testedSnapshot.resultTemplateRevision ===
      session.validation.resultTemplate.revision
  );
}
```

Expose session operations sufficient for COMMERCE-081 and COMMERCE-083 to perform these transitions:

1. **Start**
   - capture `submittedSnapshot = currentAuthoringSnapshot(session)`;
   - set `test.status = "RUNNING"`.

2. **Successful backend result with unchanged authoring snapshot**
   ```ts
   test.status = "PASSED";
   test.testedSnapshot = submittedSnapshot;
   ```

3. **Failed backend result with unchanged authoring snapshot**
   ```ts
   test.status = "FAILED";
   test.testedSnapshot = submittedSnapshot;
   ```

4. **Any backend completion after the authoring snapshot changed**
   ```ts
   test.status = "STALE";
   test.testedSnapshot = null;
   ```

A stale completion must never mark the current candidate PASSED.

COMMERCE-081 and COMMERCE-083, not C078, will invoke the existing provider backends, hold provider-specific safe Test result/diagnostic state and drive these common transitions.

Add focused regressions for:
- exact initial `NOT_RUN` state;
- exact four-revision snapshot creation;
- `PASSED` + exact matching snapshot => current pass;
- `PASSED` + any one revision mismatch => not current;
- RUNNING/FAILED/STALE never count as current pass;
- stale completion clears `testedSnapshot`;
- common Test state contains no provider payload;
- the C078 transition operations perform no provider request and call no C080/C082 Server Action.

Do not start COMMERCE-081 or COMMERCE-083 as part of this correction.

### Reviewed Files

- `src/studio/tools/new-tool-authoring-state.ts`
- `src/studio/tools/authoring-session.ts`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/tool-authoring-screen.tsx`
- `src/studio/tools/authoring/tool-authoring-tabs.tsx`
- `tests/tool-authoring-screen.test.tsx`
- `tests/external-tools-ui.test.tsx`
- submitted Attempt 3 manual screenshot showing the six-tab provider-selected flow
- C078 task Completion Report

### Validation Reviewed

- Submitted Attempt 3 packet: 4 suites, 139 tests passed.
- Submitted targeted ESLint: passed.
- Submitted changed-file diagnostics: clean.
- Submitted `git diff --check`: passed.
- Manual validation confirms the provider-navigation and pristine-session fixes.
- Source inspection confirms the requested `AuthoringTestStatus`, `AuthoringTestSnapshot`, `AuthoringTestState`, `currentAuthoringSnapshot` and `isCurrentTestPassed` common session model is not yet present.

### Architecture Conformance

Partial.

The new-Tool composition/navigation, Request ownership, Result Template integration, read-only Review separation, final Save/Cancel boundary, pristine-session semantics and persisted-DRAFT scope boundary now conform.

C078 remains incomplete only because the common session-level Test freshness/checkpoint semantics required by R9 have not yet been established.

### Follow-up

Return the same task as Attempt 4. Implement R9 only, add the focused Test-state regressions, preserve all accepted Attempt 1-3 behavior and STOP.

Do not implement or duplicate C080/C082 provider execution and do not begin COMMERCE-079, COMMERCE-081 or COMMERCE-083 until C078 is accepted Complete.
