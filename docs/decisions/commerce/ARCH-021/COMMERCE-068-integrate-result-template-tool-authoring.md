---
id: ARCH-021-COMMERCE-068
architecture_id: ARCH-021
title: Integrate Result Template into Tool authoring and Review
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 77
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-065
  - ARCH-021-COMMERCE-066
  - ARCH-021-COMMERCE-067
enables: []
created: 2026-09-27
updated: 2026-09-27
---

# Integrate Result Template into Tool authoring and Review

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Wire the reusable Result Template surface into new and persisted-DRAFT Tool authoring, remove `responseTemplate` authoring from Agent Contract, and make Review present Agent contract, Result contract and Result Template as distinct concerns while preserving the current free-navigation/local-only lifecycle.

## Context

By this task:

```text
COMMERCE-065 -> Shopify Request/Response are correctly separated
COMMERCE-066 -> ResultTemplateTab exists independently
COMMERCE-067 -> backend Agent vs Result Template validation ownership is separated
```

The remaining work is UI composition/integration. This task intentionally does **not** define the final guided traversal/gating behavior between tabs; that remains a later architecture step after all tab surfaces are implemented.

## Scope

Expected implementation areas include:

```text
src/studio/tools/new-tool-editor.tsx
src/studio/tools/tool-editor.tsx
src/studio/tools/authoring/agent-contract-tab.tsx
src/studio/tools/authoring/result-template-tab.tsx
src/studio/tools/authoring/review-tab.tsx
ToolAuthoringTabs / tab identifiers
app/styles.css only as required

tests/tool-authoring-screen.test.tsx
tests/external-tools-ui.test.tsx
tests/shopify-admin-tools-ui.test.tsx
```

## Out of Scope

- Mandatory tab order, Next/Back buttons or tab gating.
- Validation-driven automatic tab transitions.
- Explore Shopify handoff; COMMERCE-064 already owns that specific route round trip.
- Request/Response redesign beyond consuming COMMERCE-065.
- Provider execution/Test changes.
- New response-template syntax.
- Database schema changes.

## Requirements

### R1 — add Result Template as a first-class tab

Authoring tabs become conceptually:

```text
Request
Response
Result Template
Test
Agent Contract
Review
```

Use the existing free tab-navigation model. Adding the tab MUST NOT introduce gating or mandatory traversal.

### R2 — source-neutral ToolResultContract input

For both Shopify Admin and External HTTP candidates, derive/pass the current COMMERCE-063 ToolResultContract into `ResultTemplateTab` from canonical local result/output state.

React integration must not recreate provider-specific field/path walking.

### R3 — move responseTemplate authoring out of Agent Contract

Remove the Response Template JSON editor and template-specific help/validation presentation from `AgentContractTab`.

Agent Contract retains:

```text
Definition version
Agent description
Agent input schema
```

and uses COMMERCE-067's canonical Agent validator.

### R4 — Result Template owns responseTemplate local state

The dedicated tab owns editing/validation presentation for `responseTemplate` using COMMERCE-066.

For new Tools, valid template changes update only the existing local/session candidate; no Tool is persisted before final Create.

For persisted DRAFTs, editing/validating does not save automatically; the existing explicit Save boundary remains authoritative.

### R5 — preserve invalid local authoring

Invalid/incomplete Result Template input remains visible on its own tab. It must not be silently replaced by the last valid canonical template.

Final Create/Save/Publish remains responsible for rejecting a definition that cannot be canonicalized.

### R6 — Review separates three concepts

Review must present independently:

```text
Agent contract
  description + input schema (+ definition version in Tool summary as appropriate)

Result contract
  the canonical data.values schema/derived result structure

Result Template
  text/items configuration that produces renderedText
```

Do not continue displaying `responseTemplate` under the Agent contract card.

### R7 — External HTTP current behavior is preserved

The new tab consumes the current External HTTP `resultSchema` produced by Direct/Visual/JavaScript/Automatic authoring. This task does not change Response processing or Automatic inference.

### R8 — Shopify uses the derived Admin contract

The new tab consumes COMMERCE-065's compiler-derived Admin result contract; there is no manually authored Admin result schema editor.

### R9 — no final traversal coordination

Do not disable tabs based on Result Template validity, force transitions, add global Next/Back semantics or coordinate validation checkpoints across tabs beyond marking each tab's own validation stale.

## Work Items

- [ ] Add `result-template` to Tool authoring tab identifiers/order.
- [ ] Integrate `ResultTemplateTab` for new Tool authoring.
- [ ] Integrate it for persisted DRAFT authoring where the current shared tab model applies.
- [ ] Wire current source-neutral ToolResultContract into the tab.
- [ ] Remove responseTemplate editor/validation UI from Agent Contract.
- [ ] Switch Agent Contract to COMMERCE-067's canonical call-side validator.
- [ ] Update Review cards to separate Agent contract, Result contract and Result Template.
- [ ] Preserve local-only/new and explicit-save/persisted lifecycle semantics.
- [ ] Add Shopify/External parity regression tests.

## Interfaces / Contracts

Consumes:

```text
COMMERCE-065 Shopify local result contract
COMMERCE-063/066 ToolResultContract + ResultTemplateTab
COMMERCE-067 Agent validation boundary
existing External HTTP resultSchema
```

Produces no new persistent runtime contract.

## Dependencies

- `ARCH-021-COMMERCE-065`
- `ARCH-021-COMMERCE-066`
- `ARCH-021-COMMERCE-067`

## Enables

None.

## Acceptance Criteria

- [ ] Tool authoring shows a dedicated Result Template tab.
- [ ] Agent Contract no longer contains responseTemplate authoring.
- [ ] Shopify and External HTTP use the same Result Template component/contract model.
- [ ] Schema-backed tokens come from canonical ToolResultContract only.
- [ ] New Tool template edits remain non-durable until Create.
- [ ] Persisted-DRAFT template edits remain unsaved until explicit Save.
- [ ] Invalid Result Template authoring remains visible on its tab.
- [ ] Review presents Agent contract, Result contract and Result Template separately.
- [ ] External HTTP Response behavior is unchanged.
- [ ] Shopify manual GraphQL remains supported.
- [ ] All tabs remain freely navigable; no new gating/traversal coordination is introduced.

## Validation

- [ ] Tool authoring tab regression tests
- [ ] Shopify Admin UI tests
- [ ] External HTTP UI tests
- [ ] Agent Contract regression tests
- [ ] Review presentation tests
- [ ] local-vs-durable lifecycle tests
- [ ] targeted lint
- [ ] changed-file TypeScript diagnostics
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin later tab-coordination work.

## Implementation Notes

Do not use this integration task as an opportunity to implement the later traversal/gating phase. Its purpose is to compose already-defined tab capabilities only.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

None.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending review.

### Follow-up

None.
