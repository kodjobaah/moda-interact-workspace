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
status: review
priority: 77
executor: null
claimed_at: null
attempt: 1
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

- [x] Add `result-template` to Tool authoring tab identifiers/order.
- [x] Integrate `ResultTemplateTab` for new Tool authoring.
- [x] Integrate it for persisted DRAFT authoring where the current shared tab model applies.
- [x] Wire current source-neutral ToolResultContract into the tab.
- [x] Remove responseTemplate editor/validation UI from Agent Contract.
- [x] Switch Agent Contract to COMMERCE-067's canonical call-side validator.
- [x] Update Review cards to separate Agent contract, Result contract and Result Template.
- [x] Preserve local-only/new and explicit-save/persisted lifecycle semantics.
- [x] Add Shopify/External parity regression tests.

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

- [x] Tool authoring shows a dedicated Result Template tab.
- [x] Agent Contract no longer contains responseTemplate authoring.
- [x] Shopify and External HTTP use the same Result Template component/contract model.
- [x] Schema-backed tokens come from canonical ToolResultContract only.
- [x] New Tool template edits remain non-durable until Create.
- [x] Persisted-DRAFT template edits remain unsaved until explicit Save.
- [x] Invalid Result Template authoring remains visible on its tab.
- [x] Review presents Agent contract, Result contract and Result Template separately.
- [x] External HTTP Response behavior is unchanged.
- [x] Shopify manual GraphQL remains supported.
- [x] All tabs remain freely navigable; no new gating/traversal coordination is introduced.

## Validation

- [x] Tool authoring tab regression tests
- [x] Shopify Admin UI tests
- [x] External HTTP UI tests
- [x] Agent Contract regression tests
- [x] Review presentation tests
- [x] local-vs-durable lifecycle tests
- [x] targeted lint
- [x] changed-file TypeScript diagnostics
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin later tab-coordination work.

## Implementation Notes

Do not use this integration task as an opportunity to implement the later traversal/gating phase. Its purpose is to compose already-defined tab capabilities only.

## Completion Report

### Status

Ready for Architect Review

### Files Changed

Implementation repository (`moda-interact-commerce`):

- `src/studio/tools/authoring/agent-contract-tab.tsx`
- `src/studio/tools/authoring/result-template-tab.tsx`
- `src/studio/tools/authoring/review-tab.tsx`
- `src/studio/tools/authoring/tool-authoring-tabs.tsx`
- `src/studio/tools/authoring/result-template-contract-adapter.ts` (new)
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/tool-editor.tsx`
- `tests/external-tools-ui.test.tsx`
- `tests/result-template-tab.test.tsx`
- `tests/shopify-admin-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`

### Work Completed

- Added the Result Template tab to New Tool and persisted-DRAFT authoring for External HTTP and Shopify Admin, using the existing structured editor and canonical ToolResultContract compiler/validator through a shared values-envelope adapter.
- Removed response-template fields and validation responsibility from Agent Contract; both consumers now call COMMERCE-067's `validateAgentCallContractAction` with only definition version, description, and input schema.
- Review now presents Agent contract, Result contract, and Result Template independently. Admin's existing Save/Publish row and status feedback remain available across tabs; its explicit-save and publication gates are preserved.
- Preserved free tab navigation and local authoring behavior. Incomplete existing text templates retain their editable fields; invalid local buffers remain mounted across tab changes. New Tool still persists only on Create, and persisted DRAFT template edits remain unsaved until explicit Save.
- Implementation commit: `5cca63d6b056b95ebea359e69232c1e26ee0ff6f` on `task/ARCH-021-COMMERCE-068`.

### Validation Results

- Passed: `vitest run tests/tool-authoring-screen.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/external-tools-ui.test.tsx tests/result-template-tab.test.tsx` — 4 files, 127 tests.
- Passed: targeted ESLint over all 11 changed implementation and test files; no warnings or errors.
- Passed: changed-file editor diagnostics for all 11 changed files; no errors.
- Passed: `git diff --check`.
- `npm ci` was required in the fresh implementation worktree and completed. It reported the environment's Node `24.21.0` versus the package's declared `24.19.0` engine and an audit summary of 9 high-severity findings; no dependency manifests or lockfiles were changed.

### Deviations

The Shopify Admin editor keeps its established Save/Publish actions and status feedback available outside Review rather than moving the controls exclusively into Review. Review still provides the required three distinct summaries; retaining the prior action placement avoids changing the existing Admin workflow beyond C068 scope.

### Assumptions

- Shopify Admin Result Template contract input is unavailable until the persisted Admin result derivation is current; its existing Save/Publish freshness gates remain authoritative.

### Unresolved Issues

- None blocking C068 review. The npm audit and Node engine warnings above were emitted during dependency installation and are not introduced by this change.

### Architectural Concerns

None identified. No tab gating, automatic transition, traversal checkpoints, or database/gitlink changes were introduced.

### Launcher and VCS Evidence

```text
Preparation: /moda-task ARCH-021-COMMERCE-068, attempt 1, logical owner moda_commerce
Dependency gate: ARCH-021-COMMERCE-065/066/067 passed
Canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
Parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-068
Parent branch: task/ARCH-021-COMMERCE-068
Implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-068
Implementation branch: task/ARCH-021-COMMERCE-068
Parent task branch fast-forward: not-needed
Parent origin/main incorporated: already-current
Implementation task branch fast-forward: not-needed
Implementation origin/main incorporated: already-current
Recursive submodule sync/update: passed
Recorded implementation database submodule commit: 0a8d3b9feade69690b6c1e33aeda051ea588bd45
Durable claim commit: 7dc34e31f5cfac56dbdeea5159f79dc026d9fd86
Implementation commit: 5cca63d6b056b95ebea359e69232c1e26ee0ff6f
Implementation task branch pushed: yes
Parent report commit/push: this C068 report commit on the mirrored task branch
Changed implementation submodule gitlink staged in parent: no
Shared/default checkouts switched for this task: no
Implementation branch push target: explicitly corrected local upstream from origin/main to origin/task/ARCH-021-COMMERCE-068 before push
```

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
