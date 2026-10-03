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
status: review
priority: 20
executor: copilot
claimed_at: 2026-10-03T12:46:29Z
attempt: 1
depends_on:
  - ARCH-025-COMMERCE-005
enables:
  - ARCH-025-COMMERCE-007
created: 2026-10-02
updated: 2026-10-03
---

# Extract persisted Tool authoring controller

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Supplementary observations: `docs/architecture/ARCH-025-tool-editor-refactor-observations.md`

Coordinator: `moda_architect`

## Objective

Extract the complete shared persisted Tool authoring state/controller contract and make the External source-shape assertion extraction-safe without moving provider-specific editor workflows yet.

## Context

`ToolEditor` currently owns persisted candidate state, editVersion/CAS state, authoring revisions/Test freshness, Cancel/save convergence, execution-kind-local raw buffers/validation flags, dirty state, Review-validation generation fencing and authoring-session restoration in the same component that renders three execution-kind workflows. COMMERCE-007..010 must be able to consume one accepted shared controller rather than repeatedly redesigning state as each branch moves.

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

The accepted controller must own/expose the complete **mutable persisted-editor state surface currently co-located in `ToolEditor`**, because later wrappers are consume-only and shared Cancel/save convergence must not depend on reaching back into the shell. This includes: exact selected-revision resolution; selected/base/default-definition restoration; `definition`; `inputSchemaText`; `responseTemplateText`; `adminResultPathText`; `adminLiteralText`; `externalAdvancedText`; `externalSchemaText`; `parseError`; `externalValidated`; `adminValidated`; `adminResultContractFresh`; `adminMappingValid`; `externalDefinitionValid`; `resultTemplateValid`; `publishReason`; `validationMessage`; active persisted section; `editVersion`; `editorGeneration`; persisted `NewToolAuthoringState`; dirty mutation hooks; authoring revision advancement; Result Template authoring metadata; exact execution-kind-specific saved-revision convergence helpers; current Test/pass selectors; Review candidate identity/generation/action-key; duplicate in-flight Review-validation admission; and authoring-session consumption hooks.

Owning these state values does **not** make the controller the owner of External/Admin/Policy validation algorithms or provider/server actions. COMMERCE-007..009 own those calls and presentation. Later tasks must not add common/controller state; if the accepted surface is insufficient, stop and return to `moda_architect`.

### R2 — controller/provider boundary

The controller may understand the existing execution-kind-local **state shape** listed in R1 so Cancel/reset/save convergence can remain exact, but it must not invoke External HTTP, Shopify Admin or Policy provider/server validation actions. Wrappers retain provider-specific candidate construction, validation calls and presentation. The controller may expose safe state setters/convergence primitives and common primitives for wrappers to submit/settle validation against the current Review action key.

### R3 — Review validation freshness

Preserve the current canonical Review identity plus monotonic generation/in-flight action-key fencing so A→B→A never allows an old A validation to validate the later A. Preserve current pending-key semantics and stale-result suppression.

### R4 — cancel/reset exactness

Move current `cancelPersistedChanges()` semantics exactly. Restore the selected saved definition, common authoring state, input/response text, Admin result path/literals, External response-processing/result-schema buffers and editVersion; clear `parseError`, `externalValidated`, `adminValidated`, `adminResultContractFresh`, restore `adminMappingValid=true`, restore `externalDefinitionValid=true`, clear publish/validation messages and dirty state; increment editor generation; and call `onAuthoringSessionSaved`. Do **not** newly reset `resultTemplateValid` or force the active persisted section back to another tab. This exactness is why the controller owns the R1 state surface even though provider calls remain wrapper-owned.

### R5 — source-loader migration

Change only the first source-shape test loader in `external-tools-ui.test.tsx` so the existing “one persisted External DRAFT authoring implementation” assertion scans `src/studio/tools/tool-editor.tsx` plus the bounded persisted-authoring module files under `src/studio/tools/authoring/` in deterministic order. Keep the existing assertion itself and every behavioural test unchanged.

### R6 — focused controller tests

Add direct tests for authoring-session restoration, revision/Test staleness, Result Template metadata, cancel/reset, saved revision convergence, A→B→A Review fencing and duplicate validation admission.
### R7 — preserve exact authoring-session overlay semantics

Preserve the current asymmetric session overlay rather than rationalising it during extraction: the definition base is replaced from `authoringSession.definition` only for `mode === "existing"` with matching tool/revision identity; raw editor buffers (`inputSchemaText`, `responseTemplateText`, Admin result-path/literal text) currently read from the supplied session whenever those values are present; the active persisted section consults an `existing` session section without an additional tool/revision identity check; and Result Template authoring metadata is applied whenever supplied. The surrounding `ToolAuthoringScreen` is expected to provide the relevant session, but COMMERCE-006 must preserve the present ToolEditor behaviour exactly.

### R8 — preserve exact Review identity/generation implementation semantics

The Review identity remains exactly selected revision ID + editVersion + `definition` + Input Schema text + Result Template text. Do not broaden it to External/Admin raw buffers in this structural task. Preserve the current monotonic A→B→A generation and in-flight action-key fencing, including the existing bounded render-time generation update described in the observations register.

## Work Items

- [x] Add `use-persisted-tool-authoring-controller.ts` with the complete downstream contract.
- [x] Rewire the monolithic ToolEditor to consume the controller without moving execution-kind JSX/workflows yet.
- [x] Add focused controller tests.
- [x] Make only the External source-shape loader extraction-safe; retain all current assertions.
- [x] No new questionable behaviour was observed; existing documented behaviours were preserved.

## Interfaces / Contracts

Repository-internal persisted Tool authoring controller contract. `ToolEditor` remains the public compatibility boundary; no cross-repository contract is introduced.

## Dependencies

- `ARCH-025-COMMERCE-005`

## Enables

- `ARCH-025-COMMERCE-007`

## Acceptance Criteria

- [x] Existing ToolEditor public props/callers remain unchanged.
- [x] Complete shared mutable state/controller surface is sufficient for COMMERCE-007..010 without later common-controller redesign, including exact execution-kind-local Cancel/save state.
- [x] A→B→A validation and Test/revision freshness remain unchanged.
- [x] Cancel/reset preserves current exact asymmetries.
- [x] External source-shape assertion follows the bounded module set without weakening any assertion.
- [x] Frozen Admin/ToolAuthoring/new-state tests remain byte-identical and pass.

## Validation

- [x] Frozen hashes for `tests/shopify-admin-tools-ui.test.tsx`, `tests/tool-authoring-screen.test.tsx` and `tests/new-tool-authoring-state.test.ts` match the expected values.
- [x] Starting SHA-256 for `tests/external-tools-ui.test.tsx` was verified before the loader-only change.
- [x] `npx vitest run tests/persisted-tool-authoring-controller.test.tsx tests/external-tools-ui.test.tsx` passes (105 tests).
- [x] `git diff -- tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/new-tool-authoring-state.test.ts` is empty.
- [x] `npx vitest run tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/new-tool-authoring-state.test.ts` passes (198 tests).
- [ ] `npm test` exits successfully. Full-suite runs remain non-green; see Completion Report for exact outcomes and isolated reruns.
- [x] `npm run typecheck` passes.
- [x] Targeted `npm run lint -- <changed Commerce source/test files>` passes with zero errors; two existing warnings remain in untouched `code-response-panel.tsx`.
- [x] `npm run build` succeeds.
- [x] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Commerce task.

## Implementation Notes

None

## Completion Report

### Status

Ready for Review

### Files Changed

Implementation commit `4597b40` (`refactor(commerce): extract persisted tool authoring controller`):

- `src/studio/tools/authoring/use-persisted-tool-authoring-controller.ts`
- `src/studio/tools/tool-editor.tsx`
- `tests/persisted-tool-authoring-controller.test.tsx`
- `tests/external-tools-ui.test.tsx`

### Work Completed

Extracted selected-revision/default-definition restoration, all shared persisted editor state, authoring revision/Test selectors, Result Template metadata, exact Cancel/reset behavior, saved-revision convergence for Policy/External/Admin, and Review identity/generation/in-flight fencing into `usePersistedToolAuthoringController`. `ToolEditor` retains its public props and caller boundary; execution-kind JSX, validation calls and provider/server actions remain in the shell. The External source-shape test now deterministically scans `tool-editor.tsx` and sorted direct TypeScript modules under `src/studio/tools/authoring/`, with its original assertion unchanged.

Added seven direct controller tests for session overlay restoration, revision/Test staleness, Result Template metadata, Cancel/reset asymmetries, per-kind save convergence, A→B→A fencing and duplicate validation admission. Existing documented session-overlay, Cancel and External-save asymmetries were preserved; no observations-register update was required.

Implementation commit `4597b40` is pushed on `origin/task/ARCH-025-COMMERCE-006`.

### Validation Results

Launcher evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-COMMERCE-006` and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-COMMERCE-006` both use `task/ARCH-025-COMMERCE-006`. The launcher reported both worktrees synchronized with `origin/main` already current, no task-branch fast-forward needed, recursive submodule sync/update passed, and Database pinned at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`. Shared/default checkouts were not switched or edited.

- Controller plus External focused run: 105/105 passed.
- External, frozen Shopify Admin UI, frozen ToolAuthoring screen and frozen new-state suite: 198/198 passed; all three frozen SHA-256 values matched and their diff is empty.
- Additional isolated controller/External/ToolAuthoring/Admin UI run: 182/182 passed.
- Runtime-dependent request/response/QuickJS/preview validation after `npm run code-runtime:package`: 64/64 passed.
- `npm run typecheck`: passed after Prisma Client generation from the task-pinned Database submodule.
- Targeted lint: zero errors; two existing warnings in untouched `src/studio/code-response/code-response-panel.tsx`.
- `npm run build`: passed, including manual/runtime package smoke tests, Prisma generation, Next compilation and static generation.
- `git diff --check`: passed; frozen source tests remained byte-identical.
- Full `npm test` did not exit successfully. The post-build standard run reported 21 failed files / 31 failed tests / 142 passed files / 1,366 passed tests / 5 skipped files / 9 skipped tests. A structured repeat showed further full-suite run variance. The durable `ARCH025-COMMERCE-TEST-001` identities were present, including all six frozen `studio-workspace` failures and the stable Admin Explorer failures. Additional task-adjacent failures observed under whole-suite load (External UI, Shopify Admin UI and ToolAuthoring) passed on isolated rerun. The isolated non-task group passed 39/40; its only failure was `readiness-docker`'s ignored-stdio descendant timeout, an identity documented in the same baseline. No task-introduced failure reproduced in focused or isolated task-adjacent validation.

### Deviations

The full repository suite remains non-green with baseline failures and intermittent full-suite-only failures, so the corresponding Validation checkbox is intentionally left unchecked. No tests were weakened or altered beyond the explicitly authorized source loader.

### Assumptions

The latest Architect Review section was `Pending` and contained no correction requests; the launcher nevertheless marked the attempt as review-associated rework because that section exists. The original task requirements and supplementary observations remained authoritative.

### Unresolved Issues

Full-suite stability remains unresolved outside this task's bounded Commerce ToolEditor scope; see `ARCH025-COMMERCE-TEST-001` and the isolated results above. Architect review is required before enabling dependent COMMERCE-007.

### Architectural Concerns

None. The controller does not call provider/server validation actions, and execution-kind workflows remain in `ToolEditor`.

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
