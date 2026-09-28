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
status: pending
priority: 74
executor: null
claimed_at: null
attempt: 0
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

- [ ] Replace the new-Tool tab registry with the exact six-step sequence.
- [ ] Remove Agent Contract as a new-Tool authoring tab.
- [ ] Move/retain all input-schema authoring under Request for both providers.
- [ ] Wire `ResultTemplateTab` immediately after Response using production-envelope result contracts.
- [ ] Use canonical Result Template validation and stale-state semantics.
- [ ] Build a read-only derived Agent Contract Review card.
- [ ] Separate Tool Definition, Request, Result Contract, Result Template and Agent Contract in Review.
- [ ] Change new-Tool Review actions to `Cancel` + `Save`.
- [ ] Make Save use the single current Tool Definition identity/description plus the assembled candidate.
- [ ] Make Cancel abandon all local/session handoff state without persistence.
- [ ] Add exact tab-order/ownership/persistence regressions for both provider kinds.

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

- [ ] New Tool authoring exposes exactly `Tool Definition -> Request -> Response -> Result Template -> Test -> Review`.
- [ ] Agent Contract is absent from the tab list.
- [ ] External and Shopify input schemas are authored only from Request.
- [ ] Result Template is authored only from its dedicated tab and edits the canonical `responseTemplate`.
- [ ] External template bindings include production `values` paths rather than inner-schema-only paths.
- [ ] Shopify template bindings come from the Admin compiler output contract.
- [ ] Review shows Agent Contract read-only and contains no template editor/template JSON under Agent Contract.
- [ ] Review shows Result Template separately.
- [ ] New Tool final buttons are `Cancel` and `Save`.
- [ ] Save performs exactly one final create operation; Cancel performs none.
- [ ] No edit/validation/tab navigation before Save creates durable Tool state.
- [ ] Existing Shopify Explore round-trip and current Request/Response authoring remain functional.

## Validation

- [ ] `npx vitest run tests/tool-authoring-screen.test.tsx tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/result-template-tab.test.tsx`
- [ ] focused assertions for exact tab order and absence of Agent Contract tab
- [ ] focused assertions for Request-owned input schema for External + Shopify
- [ ] focused assertions for production-envelope Result Template bindings
- [ ] focused Save-once / Cancel-zero-write tests
- [ ] targeted ESLint for changed files
- [ ] changed-file TypeScript diagnostics, or repository typecheck with baseline reconciliation
- [ ] `git diff --check`

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not begin an enabled or adjacent task.

## Implementation Notes

Do not delete `AgentContractTab` solely because new Tool authoring no longer uses it; persisted/legacy consumers are handled by COMMERCE-079. It may become removable only when that follow-up proves no supported consumer remains.

The flow is ordered for comprehension, not as a full wizard gate. After provider selection, existing free tab navigation may remain unless a tab cannot safely render without required local provider state.

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
