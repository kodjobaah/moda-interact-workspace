---
id: ARCH-025-COMMERCE-006
architecture_id: ARCH-025
title: Extract persisted Tool authoring controller
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-COMMERCE-005
enables:
  - ARCH-025-COMMERCE-007
created: 2026-10-02
updated: 2026-10-02
---

# Extract persisted Tool authoring controller

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Supplementary observations: `docs/architecture/ARCH-025-tool-editor-refactor-observations.md`

Coordinator: `moda_architect`

## Objective

Extract the complete execution-kind-neutral persisted Tool authoring state/controller contract and make the External source-shape assertion extraction-safe without moving provider-specific editor workflows yet.

## Context

`ToolEditor` currently owns persisted candidate state, editVersion/CAS state, authoring revisions/Test freshness, shared cancel/reset/save convergence, dirty state, Review-validation generation fencing and authoring-session restoration in the same component that renders three execution-kind workflows. COMMERCE-007..010 must be able to consume one accepted shared controller rather than repeatedly redesigning state as each branch moves.

## Scope

Authorised implementation surface:

```text
src/studio/tools/tool-editor.tsx
src/studio/tools/authoring/use-persisted-tool-authoring-controller.ts
tests/persisted-tool-authoring-controller.test.tsx
tests/external-tools-ui.test.tsx
```

## Out of Scope

Policy/External/Admin workflow extraction, specialised editor changes, server-action changes, publication-rule cleanup, observed-issue fixes or generic plugin architecture.

## Requirements

### Common ARCH-025 ToolEditor invariants

- This is a **move-only structural refactor**. Do not change Tool authoring product behaviour, server-action signatures/authorization, publication semantics, provider protocols, Test checkpoint rules, CAS/editVersion semantics, Result Template semantics or execution-kind contracts.
- Preserve `ToolEditor` at `src/studio/tools/tool-editor.tsx` with the same public props/caller boundary. Existing `ToolAuthoringScreen` and Studio callers do not migrate.
- Preserve persisted DRAFT execution-kind dispatch for `POLICY_OPERATION`, `EXTERNAL_HTTP` and `SHOPIFY_ADMIN_GRAPHQL`, plus the existing published/no-revision/defensive-generic paths.
- Preserve the six persisted authoring tabs and default persisted tab `request` unless an existing authoring session contains one of the accepted persisted sections.
- Preserve `new-tool-authoring-state.ts` as the canonical Test/revision/result-template freshness engine. Do not invent another revision/checkpoint model in the controller or wrappers.
- Preserve Test freshness/STALE transitions, candidate/revision identity, transient Test argument/shop semantics and the exact requirement that saved/published evidence belongs to the current candidate.
- Preserve Review-validation generation fencing including A→B→A protection and duplicate in-flight suppression. Do not reduce it to canonical-value equality alone.
- Preserve current execution-kind-specific validation/action ownership. The shared controller owns common candidate/revision/reset/save convergence state; External/Admin/Policy wrappers own their existing provider/execution-kind validation calls and presentation.
- Preserve current save/cancel/publish asymmetries documented in `docs/architecture/ARCH-025-tool-editor-refactor-observations.md`. They are follow-up observations, not authority to normalize behaviour in ARCH-025.
- Preserve immutable Policy Operation MCP name and operation/operationVersion binding, External connection-revision pinning, and Shopify Admin schema/result-contract identity rules.
- Preserve `SUPER_ADMIN` publication gating and current publication-reason behaviour per execution kind.
- Preserve `StudioComposerContext` authoring-session handoffs and the exact existing Explore Shopify return payload. Do not redesign Studio navigation or authoring-session ownership.
- Reuse existing specialised owners: `policy-operation-editor.tsx`, `external-http/editor.tsx`, `shopify-admin-editor.tsx`, `shopify-admin-response-editor.tsx`, `authoring/result-template-tab.tsx`, `authoring/review-tab.tsx`, `authoring/shopify-admin-test-tab.tsx`, `authoring/tool-authoring-tabs.tsx`, `authoring/tool-authoring-step-navigation.tsx` and `new-tool-authoring-state.ts`.
- Do not create a generic execution-kind plugin/registration framework, new state store, command bus or DI framework solely for this extraction.
- These tests are frozen byte-for-byte throughout COMMERCE-006..010: `tests/shopify-admin-tools-ui.test.tsx` (`d856cac3626605670e08a21826cfcc1a8e6595dcffc764e20d9ef59c2ff78446`), `tests/tool-authoring-screen.test.tsx` (`2245e54996589f7289639bb28c6b364f1726ec291debec390e208a5c304b6c20`) and `tests/new-tool-authoring-state.test.ts` (`267352261520b38eaa9845f93dc09eb8860e75a4010d9da26827c6617bcdcf63`).
- `tests/external-tools-ui.test.tsx` starts at SHA-256 `97ffbc70e29d4ff60a48e5aabd0ff3faec6dea7984ed0f239fcb4a8fc868f4d3`. COMMERCE-006 may change only its bounded source-loading mechanism for the existing “one persisted External DRAFT implementation” assertion; all other assertions/behaviour remain unchanged. COMMERCE-007..010 must not modify the accepted COMMERCE-006 version.
- No task may weaken, skip, delete or rewrite assertions merely to accommodate extraction.

### R1 — complete shared controller contract

The accepted controller must own/expose every common value/action required by COMMERCE-007..010: selected revision/base restoration; definition and raw JSON buffers; editVersion; editor generation; persisted `NewToolAuthoringState`; active persisted section; shared parse/validation/publish message state where execution-kind-neutral; dirty mutation hooks; authoring revision advancement; Result Template authoring metadata; cancel/reset; saved-revision convergence helpers; current Test/pass selectors; Review candidate identity/generation/action-key; duplicate in-flight Review-validation admission; and authoring-session consumption hooks. Later tasks are consume-only. If a missing common controller interface is discovered later, stop and return it to `moda_architect` rather than expanding accepted controller scope.

### R2 — controller/provider boundary

The controller must not invoke External HTTP, Shopify Admin or Policy provider/server validation actions. Wrappers retain provider-specific candidate construction/validation calls and presentation. The controller may expose safe common primitives for wrappers to submit/settle validation against the current Review action key.

### R3 — Review validation freshness

Preserve the current canonical Review identity plus monotonic generation/in-flight action-key fencing so A→B→A never allows an old A validation to validate the later A. Preserve current pending-key semantics and stale-result suppression.

### R4 — cancel/reset exactness

Move current `cancelPersistedChanges()` semantics exactly, including the existing asymmetries documented in the observations file: restore the selected saved definition/state/editVersion and clear the same validation/dirty fields; increment editor generation; call `onAuthoringSessionSaved`; do **not** newly reset `resultTemplateValid` or force `externalSection` back to another tab.

### R5 — source-loader migration

Change only the first source-shape test loader in `external-tools-ui.test.tsx` so the existing “one persisted External DRAFT authoring implementation” assertion scans `src/studio/tools/tool-editor.tsx` plus the bounded persisted-authoring module files under `src/studio/tools/authoring/` in deterministic order. Keep the existing assertion itself and every behavioural test unchanged.

### R6 — focused controller tests

Add direct tests for authoring-session restoration, revision/Test staleness, Result Template metadata, cancel/reset, saved revision convergence, A→B→A Review fencing and duplicate validation admission.

## Work Items

- [ ] Add `use-persisted-tool-authoring-controller.ts` with the complete downstream contract.
- [ ] Rewire the monolithic ToolEditor to consume the controller without moving execution-kind JSX/workflows yet.
- [ ] Add focused controller tests.
- [ ] Make only the External source-shape loader extraction-safe; retain all current assertions.
- [ ] Record any observed behaviour that looks questionable in the supplementary observations document rather than fixing it.

## Interfaces / Contracts

Repository-internal persisted Tool authoring controller contract. `ToolEditor` remains the public compatibility boundary; no cross-repository contract is introduced.

## Dependencies

- `ARCH-025-COMMERCE-005`

## Enables

- `ARCH-025-COMMERCE-007`

## Acceptance Criteria

- [ ] Existing ToolEditor public props/callers remain unchanged.
- [ ] Complete shared state/controller surface is sufficient for COMMERCE-007..010 without later common-controller redesign.
- [ ] A→B→A validation and Test/revision freshness remain unchanged.
- [ ] Cancel/reset preserves current exact asymmetries.
- [ ] External source-shape assertion follows the bounded module set without weakening any assertion.
- [ ] Frozen Admin/ToolAuthoring/new-state tests remain byte-identical and pass.

## Validation

- [ ] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/shopify-admin-tools-ui.test.tsx':'d856cac3626605670e08a21826cfcc1a8e6595dcffc764e20d9ef59c2ff78446','tests/tool-authoring-screen.test.tsx':'2245e54996589f7289639bb28c6b364f1726ec291debec390e208a5c304b6c20','tests/new-tool-authoring-state.test.ts':'267352261520b38eaa9845f93dc09eb8860e75a4010d9da26827c6617bcdcf63'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected frozen hashes.
- [ ] `node -e "const fs=require('node:fs'),c=require('node:crypto');const p='tests/external-tools-ui.test.tsx',x='97ffbc70e29d4ff60a48e5aabd0ff3faec6dea7984ed0f239fcb4a8fc868f4d3';console.log(c.createHash('sha256').update(fs.readFileSync(p)).digest('hex')===x?'starting External suite hash verified':'External suite baseline changed')"` is recorded before the loader-only change.
- [ ] `npx vitest run tests/persisted-tool-authoring-controller.test.tsx tests/external-tools-ui.test.tsx` passes.
- [ ] `git diff -- tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/new-tool-authoring-state.test.ts` is empty.
- [ ] `npx vitest run tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/new-tool-authoring-state.test.ts` passes.
- [ ] `npm test` passes without task-introduced regression.
- [ ] `npm run typecheck` passes.
- [ ] targeted `npm run lint -- <changed Commerce source/test files>` (or repository-equivalent targeted ESLint invocation using the declared lint script) passes.
- [ ] `npm run build` succeeds.
- [ ] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Commerce task.

## Implementation Notes

None

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

Pending.

### Follow-up

None
