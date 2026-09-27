---
id: ARCH-021-COMMERCE-076
architecture_id: ARCH-021
title: Restore Result Template tab integration after authoring regression
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 78
executor: null
claimed_at: null
attempt: 0
depends_on:
enables: []
created: 2026-09-27
updated: 2026-09-27
---

# Restore Result Template tab integration after authoring regression

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Restore the already-accepted COMMERCE-068 Result Template authoring boundary in the current Tool editor: expose a dedicated Result Template tab for new and persisted-DRAFT External HTTP and Shopify Admin Tools, keep Agent Contract call-side only, and restore Review separation without changing Request, Response, live Test, persistence or navigation/gating behaviour.

## Context

COMMERCE-068 was architect-accepted Complete and established these invariants:

```text
Agent Contract
  definition version
  agent description
  agent input schema

Result Template
  responseTemplate authoring
  ToolResultContract-backed token bindings
  template validation

Review
  Agent contract
  Result contract
  Result Template
```

The current repository snapshot has regressed that accepted composition while retaining the underlying Result Template capability:

```text
src/studio/tools/authoring/result-template-tab.tsx
  still exists

src/studio/tools/authoring/tool-authoring-tabs.tsx
  exposes only Request / Response / Test / Agent contract / Review

src/studio/tools/authoring/agent-contract-tab.tsx
  again owns Agent response template authoring and compatibility validation

src/studio/tools/new-tool-editor.tsx
  does not render ResultTemplateTab and Review again displays responseTemplate under Agent contract

src/studio/tools/tool-editor.tsx
  persisted Shopify Admin authoring again places Response template under Agent contract
```

This is a bounded post-acceptance regression correction. Do not redesign Result Template semantics or use this task to implement the separate navigation/readiness phase.

COMMERCE-055 is included only as a sequencing dependency because it changes the current new-Tool Test/editor composition. This task must preserve that accepted live-Test UI rather than racing the same authoring files.

## Scope

Primary implementation areas:

```text
src/studio/tools/authoring/tool-authoring-tabs.tsx
src/studio/tools/authoring/agent-contract-tab.tsx
src/studio/tools/authoring/result-template-tab.tsx        # consume; change only if integration requires it
src/studio/tools/authoring/review-tab.tsx                  # consume/change only for restored separation
src/studio/tools/new-tool-editor.tsx
src/studio/tools/tool-editor.tsx
```

A small source-neutral Result Template contract adapter/helper may be restored or recreated if required to connect canonical result schemas to COMMERCE-063 `ToolResultContract` without provider-specific field walking.

Focused regressions are expected in:

```text
tests/tool-authoring-screen.test.tsx
tests/external-tools-ui.test.tsx
tests/shopify-admin-tools-ui.test.tsx
tests/result-template-tab.test.tsx                         # only when integration needs additional proof
```

## Out of Scope

- New Result Template syntax or token semantics.
- Changes to COMMERCE-063 result-contract compilation/validation.
- Request or Response authoring behaviour.
- External HTTP or Shopify Admin live-Test behaviour.
- Provider execution, networking or credentials.
- New Tool persistence semantics.
- Persisted-DRAFT Save/Publish semantics.
- Previous/Next controls, readiness aggregation, locked tabs or mandatory traversal.
- Automatic Response generation.
- Database, Shared, Gateway or deployment changes.
- Opportunistic cleanup of unrelated authoring code.

## Requirements

### R1 — restore a six-tab Tool authoring surface

Both supported Tool kinds must expose the same dedicated Result Template step in new-Tool and persisted-DRAFT authoring.

Preserve the current accepted relative order of the existing five tabs and insert Result Template immediately before Review:

```text
Request
Response
Test
Agent contract
Result template
Review
```

`ToolAuthoringTabId` and the shared tab registry must represent `result-template` explicitly. Do not create provider-specific duplicate tab registries.

Tab selection remains free. This task does not add gating or mandatory traversal.

### R2 — Agent Contract is call-side only again

Restore the COMMERCE-067/C068 ownership boundary.

Agent Contract contains only:

```text
Definition version
Agent description
Agent input schema
```

It must use the canonical call-side Agent validator (`validateAgentCallContractAction` or the current equivalent) and must not accept/validate/display:

```text
responseTemplate
output/result schema solely for template compatibility
Result Template issues
```

Remove the regressed `Agent response template` control from this tab for both new and persisted-DRAFT flows.

### R3 — Result Template owns responseTemplate authoring

Render the existing COMMERCE-066 `ResultTemplateTab` on the dedicated tab for:

```text
External HTTP new Tool
External HTTP persisted DRAFT
Shopify Admin new Tool
Shopify Admin persisted DRAFT
```

The tab edits the same canonical `definition.responseTemplate`; do not introduce a second template state model.

For new Tools, valid template changes update only the existing local/session candidate and remain non-durable until final Create.

For persisted DRAFTs, template edits remain unsaved until the existing explicit Save boundary.

Invalid/incomplete Result Template local authoring must remain visible on that tab according to the accepted COMMERCE-066 behaviour.

### R4 — consume the current source-neutral ToolResultContract

Compile/pass the current canonical result contract into `ResultTemplateTab` through COMMERCE-063 semantics.

For External HTTP, derive from the current Response result schema.

For Shopify Admin, derive from the current compiler-produced Admin result schema/result contract.

Do not reimplement provider-specific schema walking in React. Restore/reuse the accepted source-neutral adapter shape where necessary.

Changing the underlying result contract must make prior Result Template validation stale according to existing `ResultTemplateTab` semantics.

### R5 — Review separates Agent contract, Result contract and Result Template

Review must again show these as distinct concepts:

```text
Agent contract
  definition/description/input schema summary

Result contract
  canonical processed-result schema/structure

Result Template
  current text/items template configuration
```

Do not display `responseTemplate` under the Agent contract card.

Keep Request/Response/Test Review information and current Create/Save/Publish actions unchanged except where composition is necessary to restore the three-way separation.

### R6 — preserve the current live Test and authoring lifecycle

The completed/live-Test work present when this task starts must remain intact.

In particular, this task must not:

- replace or remove the Test tab/components;
- change live-Test execution contracts;
- create durable Tool state during new-Tool tab editing;
- auto-save persisted DRAFT template edits;
- alter current Request/Response validation semantics.

### R7 — regression guard must prove the integration cannot disappear silently

Add focused tests that fail if the dedicated Result Template integration is removed again.

At minimum prove:

1. the shared tab registry exposes exactly the six expected authoring tabs including `Result template`;
2. new External HTTP authoring renders `ResultTemplateTab` and no response-template field under Agent Contract;
3. new Shopify Admin authoring has the same separation;
4. persisted-DRAFT External HTTP authoring has the same separation;
5. persisted-DRAFT Shopify Admin authoring has the same separation;
6. Review presents Agent contract, Result contract and Result Template separately;
7. Result Template edits retain existing local-vs-durable semantics;
8. the existing Test tab remains present and functional after the restoration.

Do not satisfy the regression only through snapshots or static string assertions when an executable user-facing assertion is practical.

## Work Items

- [ ] Restore `result-template` to the shared Tool authoring tab identifier/registry.
- [ ] Restore call-side-only Agent Contract composition and validation.
- [ ] Restore ResultTemplateTab integration for new External HTTP authoring.
- [ ] Restore ResultTemplateTab integration for new Shopify Admin authoring.
- [ ] Restore ResultTemplateTab integration for persisted External HTTP DRAFT authoring.
- [ ] Restore ResultTemplateTab integration for persisted Shopify Admin DRAFT authoring.
- [ ] Restore the source-neutral ToolResultContract adapter/wiring required by the tab.
- [ ] Restore Review separation of Agent contract, Result contract and Result Template.
- [ ] Add six-tab/provider/lifecycle regression coverage that would catch this integration disappearing again.
- [ ] Verify current live Test behaviour is preserved.

## Interfaces / Contracts

Consumes the already-accepted boundaries from:

```text
ARCH-021-COMMERCE-063
ToolResultContract compilation and Result Template validation

ARCH-021-COMMERCE-066
ResultTemplateTab authoring component

ARCH-021-COMMERCE-067
call-side Agent validation ownership

ARCH-021-COMMERCE-068
accepted Result Template integration semantics

ARCH-021-COMMERCE-055
current External HTTP Test-tab composition that must be preserved
```

No new persistent or cross-repository runtime contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-055
- ARCH-021-COMMERCE-068

## Enables

None.

## Acceptance Criteria

- [ ] New and persisted-DRAFT Tool authoring expose six shared tabs: Request, Response, Test, Agent contract, Result template, Review.
- [ ] Both External HTTP and Shopify Admin expose the dedicated Result Template tab.
- [ ] Agent Contract contains no responseTemplate authoring or Result Template validation responsibility.
- [ ] Agent Contract uses the canonical call-side validation boundary.
- [ ] ResultTemplateTab edits the existing canonical `definition.responseTemplate` rather than a parallel model.
- [ ] Result Template tokens/bindings derive from the current COMMERCE-063 ToolResultContract for both providers.
- [ ] Invalid local Result Template authoring remains visible for correction.
- [ ] New Tool Result Template edits remain non-durable until final Create.
- [ ] Persisted-DRAFT Result Template edits remain unsaved until explicit Save.
- [ ] Review presents Agent contract, Result contract and Result Template separately.
- [ ] Existing Request, Response and live Test behaviour remains unchanged.
- [ ] Tabs remain freely selectable; no Previous/Next, readiness gating or mandatory traversal is introduced.
- [ ] Focused regression tests fail if the Result Template tab/composition is removed again.

## Validation

- [ ] focused shared tab-registry/new-Tool authoring tests
- [ ] focused persisted-DRAFT Tool authoring tests
- [ ] focused External HTTP UI regressions
- [ ] focused Shopify Admin UI regressions
- [ ] focused Agent Contract/Result Template/Review regressions
- [ ] existing live Test UI regressions affected by changed authoring composition
- [ ] targeted ESLint for changed files
- [ ] changed-file TypeScript diagnostics or repository typecheck with baseline reconciliation
- [ ] `git diff --check`

## Stop Condition

After the dedicated Result Template integration and regression coverage are restored, set the task to `review`, complete the Completion Report and STOP. Do not begin navigation/readiness work or unrelated authoring refactors.

## Implementation Notes

This is a regression-restoration task, not a redesign. Prefer reconstructing the already-accepted C068 composition from the surviving COMMERCE-063/066/067 boundaries rather than inventing new template semantics.

The historical C068 tab order placed Result Template earlier in the flow. The current product flow has since established Request -> Response -> Test -> Agent contract -> Review. For this bounded restoration, preserve that current order and insert Result Template immediately before Review; later navigation/readiness work owns guided traversal semantics.

If implementation reveals that a later accepted task intentionally removed the C068 boundary for a documented architectural reason, stop and return that evidence to `moda_architect` rather than silently overriding it.

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
