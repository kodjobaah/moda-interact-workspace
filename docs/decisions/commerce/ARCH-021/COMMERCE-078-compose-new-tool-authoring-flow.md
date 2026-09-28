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
status: in_progress
priority: 74
executor: copilot
claimed_at: 2026-09-28T10:22:02Z
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

## Validation

- [x] `npx vitest run tests/tool-authoring-screen.test.tsx tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/result-template-tab.test.tsx`
- [x] focused assertions for exact tab order and absence of Agent Contract tab
- [x] focused assertions for Request-owned input schema for External + Shopify
- [x] focused assertions for production-envelope Result Template bindings
- [x] focused Save-once / Cancel-zero-write tests
- [x] targeted ESLint for changed files
- [x] changed-file TypeScript diagnostics, or repository typecheck with baseline reconciliation
- [x] `git diff --check`

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not begin an enabled or adjacent task.

## Implementation Notes

Do not delete `AgentContractTab` solely because new Tool authoring no longer uses it; persisted/legacy consumers are handled by COMMERCE-079. It may become removable only when that follow-up proves no supported consumer remains.

The flow is ordered for comprehension, not as a full wizard gate. After provider selection, existing free tab navigation may remain unless a tab cannot safely render without required local provider state.

## Completion Report

### Status

Attempt 2 complete; resubmitted for Architect Review.

### Execution Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent task worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-078`, `task/ARCH-021-COMMERCE-078`
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-078`, `task/ARCH-021-COMMERCE-078`
- Shared workspace and implementation reference checkouts were not switched or modified; no other task worktree was reused.
- Parent task remote branch fast-forwarded: not-needed; `origin/main` incorporated: yes.
- Implementation remote task branch fast-forwarded: not-needed; `origin/main` incorporated: already-current.
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

### Validation Results

- Required Vitest command passed on Attempt 2: 4 files, 135 tests.
- Targeted ESLint passed for all Attempt 2 changed implementation and test files.
- Editor diagnostics reported no errors in any Attempt 2 changed C078 file.
- `git diff --check` passed.
- `npm run typecheck` remains non-green due existing repository diagnostics outside the C078 changes, including untouched integration services, persisted tool-editor call sites, and result-contract tests; the changed C078 files have no editor diagnostics.

### Deviations

The full repository typecheck has an existing non-green baseline from Attempt 1; Attempt 2 introduced no editor diagnostics in changed files and did not broaden into unrelated files.

### Assumptions

Existing Agent Contract consumers remain supported; persisted-DRAFT parity stays with COMMERCE-079.

### Unresolved Issues

No unresolved C078 implementation or validation issues. The repository-wide typecheck baseline remains as noted above.

### Architectural Concerns

None identified.

## Architect Review

### Review Status

Changes Requested

### Review Notes

This amended Attempt 2 review supersedes the earlier Attempt 2 review wording.

Attempt 2 successfully fixes both findings from Attempt 1:

1. persisted External and Shopify DRAFT authoring retains the pre-C078 composition and Agent Contract remains available until COMMERCE-079; and
2. External Request now renders `Input JSON Schema` before the connection/request mapping controls.

Those corrections are accepted.

Manual validation and source inspection exposed two remaining C078 defects. The intended new-Tool navigation behavior is now clarified as follows.

#### 1. Navigation visibility is controlled only by whether a Tool type/provider has been committed

The blank new-Tool authoring session may show only `Tool Definition`. This is acceptable and preferred.

While no Tool type/provider has been committed:

- show only the `Tool Definition` tab;
- show clear instructional copy explaining that the operator must select a Tool type before the remaining authoring tabs become available;
- do not expose Request/Response/Result Template/Test/Review provider-specific surfaces yet.

Use instructional copy equivalent to:

> Select a Tool type to continue. Request, Response, Result Template, Test and Review become available after a Tool type is selected.

Once either supported provider is committed:

- `Shopify Admin GraphQL`; or
- `External HTTP/API`;

the new-Tool page must immediately expose exactly:

```text
Tool Definition -> Request -> Response -> Result Template -> Test -> Review
```

Visibility of those five downstream tabs must depend only on a committed Tool type/provider. It must **not** depend on MCP name, display name, description, definition version or the rest of Tool Definition being schema-valid.

The current implementation still couples downstream-tab visibility to `showWorkspace`, which is based on a schema-valid provider definition. The submitted manual screenshots demonstrate that selecting Shopify Admin GraphQL or External HTTP/API still leaves only `Tool Definition` visible when the other definition fields are blank.

Provider-dependent tabs may reject/disable actions that require missing local state, but they must be visible after provider selection.

Provider switching must preserve committed-provider semantics:

- choosing another Tool type while a provider is already committed must not replace the committed provider until the destructive reset is explicitly confirmed;
- while confirmation is pending, the existing provider remains committed and its six-tab navigation remains visible;
- `Cancel` retains the original provider and authoring state;
- `Reset and change Tool type` commits the new provider, clears the provider-owned downstream state as already designed, and keeps the same six-tab navigation visible.

#### 2. Opening the blank local authoring session must not make it dirty

`ToolAuthoringScreen` currently launches the local session with an immediate dirty transition. This causes `Back` to display `Discard unsaved changes?` even when the operator has entered nothing.

Creating the blank browser-local session is not an authoring mutation.

Required behavior:

- `Create Tool` opens the blank local authoring session with `Tool Definition` active and `dirty = false`;
- `Back` immediately after `Create Tool`, before any user mutation, returns to `/tools` without a discard dialog and without any durable write;
- selecting a Tool type/provider is a real authoring mutation and may mark the session dirty;
- edits to Tool Definition, Request, Response, Result Template or other canonical authoring state remain real mutations and must continue to trigger the existing discard protection;
- after the first real mutation, `Back` must still show the existing discard confirmation.

Add focused regressions proving all of the following:

1. `Create Tool` with no provider selected:
   - only `Tool Definition` is present in the tablist;
   - the provider-selection instructional message is visible;
   - `Back` returns to `/tools` without a discard dialog;
   - no Tool/create persistence action is called.

2. Selecting `Shopify Admin GraphQL` with MCP name/display name/description still blank:
   - immediately exposes exactly `Tool Definition -> Request -> Response -> Result Template -> Test -> Review`;
   - downstream tab visibility does not require the rest of Tool Definition to validate.

3. Selecting `External HTTP/API` with identity fields still blank:
   - immediately exposes the same six tabs.

4. Provider switch confirmation:
   - Shopify committed -> choose External -> before confirmation, Shopify remains the committed provider and six tabs remain visible;
   - `Cancel` preserves Shopify and its state;
   - `Reset and change Tool type` commits External, clears provider-owned downstream state and leaves the six tabs visible.

5. Dirty navigation:
   - pristine session -> Back has no confirmation;
   - after provider selection or another real edit -> Back shows `Discard unsaved changes?`.

6. Attempt 1 corrections remain protected:
   - persisted External/Shopify DRAFT composition remains unchanged by C078 and retains Agent Contract until C079;
   - External `Input JSON Schema` remains before connection/request mapping controls.

No persisted-DRAFT migration, provider networking, Result Template grammar change, database change, COMMERCE-079 implementation, COMMERCE-081 implementation or COMMERCE-083 implementation is requested.

### Reviewed Files

- `src/studio/tools/authoring/tool-authoring-tabs.tsx`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/tool-authoring-screen.tsx`
- `src/studio/tools/new-tool-authoring-state.ts`
- `tests/tool-authoring-screen.test.tsx`
- `tests/external-tools-ui.test.tsx`
- submitted manual screenshots showing:
  - only Tool Definition before provider selection;
  - only Tool Definition after Shopify Admin GraphQL selection;
  - only Tool Definition after External HTTP/API selection;
  - pristine Back triggering the discard dialog.

### Validation Reviewed

- Submitted Attempt 2 packet: 4 suites, 135 tests passed.
- Submitted targeted ESLint: passed.
- Submitted changed-file diagnostics: clean.
- Submitted `git diff --check`: passed.
- Attempt 1 corrections were confirmed in source/tests.
- Manual validation exposes the two remaining defects above.
- Source inspection confirms downstream-tab visibility is still gated by overall definition validity rather than committed provider presence, and the blank launcher path marks the new session dirty immediately.

### Architecture Conformance

Partial.

The C078 ownership model, persisted-DRAFT boundary, External Request schema placement, Result Template contract, Review separation and Save persistence boundary are aligned.

C078 is not accepted until:

1. blank new-Tool authoring provides explicit provider-selection guidance and remains clean;
2. committing a Tool type/provider immediately reveals the complete six-tab new-Tool navigation independently of the remaining Tool Definition validity; and
3. the discard guard activates only after a real authoring mutation.

### Follow-up

Return the same task as Attempt 3. Implement only the corrections defined above and add the focused regressions. Do not start COMMERCE-079, COMMERCE-081 or COMMERCE-083 until C078 is accepted Complete.
