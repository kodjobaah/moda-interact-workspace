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
claimed_at: 2026-10-03T14:35:16Z
attempt: 2
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
- [x] `npm test` completes without a task-introduced regression under `ARCH025-COMMERCE-TEST-001`; every new, changed or worsened failing identity is investigated.
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

Launcher evidence for Attempt 2: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-COMMERCE-006` and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-COMMERCE-006` both use `task/ARCH-025-COMMERCE-006`. Dependency `ARCH-025-COMMERCE-005` was `complete`; dependency gate passed. Parent and implementation task branches needed no remote fast-forward and already incorporated `origin/main`. Recursive submodule sync and update passed; Database was materialised at `201e0a7044e7ab20d21538487816163ade2233b0`. The launcher claimed Attempt 2 for `copilot` at `2026-10-03T14:35:16Z`; durable parent claim commit `70e346f7ca97fa38cf257deaa74232bab0b6fb7c` was pushed. Shared/default checkouts were not switched or edited.

Attempt 2 made no implementation source/test changes. Final implementation task-branch `HEAD` was `3ef3cf3e99f2d48f2e5b22be595b0d9161443adc`, equal to `origin/task/ARCH-025-COMMERCE-006`; its worktree was clean after validation. The parent report branch was at claim commit `70e346f7ca97fa38cf257deaa74232bab0b6fb7c`, equal to its origin task ref before this completion-report update. The completion-report commit was pushed, and the final handoff verifies the resulting local/remote parent refs and clean worktree.

- Controller plus External focused run: 105/105 passed.
- External, frozen Shopify Admin UI, frozen ToolAuthoring screen and frozen new-state suite: 198/198 passed; all three frozen SHA-256 values matched and their diff is empty.
- Additional isolated controller/External/ToolAuthoring/Admin UI run: 182/182 passed.
- Runtime-dependent request/response/QuickJS/preview validation after `npm run code-runtime:package`: 64/64 passed.
- `npm run typecheck`: passed after Prisma Client generation from the task-pinned Database submodule.
- Targeted lint: zero errors; two existing warnings in untouched `src/studio/code-response/code-response-panel.tsx`.
- `npm run build`: passed, including manual/runtime package smoke tests, Prisma generation, Next compilation and static generation.
- `git diff --check`: passed; frozen source tests remained byte-identical.
- Attempt 2 full `npm test` (Vitest JSON reporter, `/tmp/commerce006-attempt2-fullsuite.json`) reported 20 failed files / 30 failed tests / 143 passed files / 1,367 passed tests / 5 skipped files / 9 skipped tests. Each of the 30 failing test identities below is class (a), a stable failure listed in `ARCH025-COMMERCE-TEST-001`; all six collection failures are also stable baseline entries. No class (c) out-of-baseline identity appeared.

  - `tests/admin-explorer.test.tsx`: preserves a valid manual query that is not representable and returns it unchanged; builds and validates a representable selection before merging query fields into an existing draft; keeps exact raw text for an unchanged literal mapping and drops stale buffers; round-trips a newly visual-authored string literal through the New Tool Request editor; validates Request query while preserving malformed unrelated editor buffers; shows validation progress while the Shopify Admin validation request is in flight; validates a restored visual selection even when the selected root field is outside the loaded schema page; keeps Validate available when the visual candidate cannot yet be built and reports the blocking reason; offers a return action beside validation without applying temporary Explorer state; cancel returns to the validated origin without merging temporary Explorer state.
  - `tests/admin-graphql-compiler.test.ts`: rejects nullable input schemas for non-null variables.
  - `tests/agent-configuration-retained-read.test.ts`: tracks model and prompt CAS versions on one retained row across clear operations.
  - `tests/agent-contract-validation.test.ts`: rejects unknown scalar paths and non-list items paths.
  - `tests/auth-entrypoints.test.ts`: keeps NextAuth and health public while the MCP route remains private.
  - `tests/backend-postgres-rehearsal.test.ts`: publishes once, replays durably, rejects stale CAS, races across connections, and rolls back injected failure.
  - `tests/discount-evaluator.test.ts`: retains preview purpose, environment, and trace correlation in eligibility telemetry.
  - `tests/discovery-limits.test.ts`: allows 60 sequential requests and rejects the 61st in the rolling window.
  - `tests/health.test.ts`: readiness checks required dependencies and has no release-publication dependency; bounds hanging dependencies under two seconds and aborts Redis.
  - `tests/merchant-knowledge-embedding.test.ts`: validates the exact OpenAI provenance environment contract.
  - `tests/policy-operation-authoring-server-actions.test.ts`: returns UNAVAILABLE for invalid or unregistered operation identities without fallback.
  - `tests/policy-operation-result-template.test.ts`: reports whether each currently registered operation result is template-compatible.
  - `tests/preview-page.test.tsx`: projects only browser-safe selected-Shop configuration and Feature fields; never forwards an invalid URL Shop ID as the selected Shop.
  - `tests/studio-workspace.test.tsx`: exposes the failure class when a named Studio action rejects unexpectedly; authors a reusable tool without publishing and navigates to its returned ID; retains incremental invalid JSON and saves only the complete canonical tool definition; resets editor state when a mounted detail changes to another record; keeps newer edits dirty when an earlier save completes; retains editor input after stale CAS.

  Collection failures (class (a), each listed in the same baseline): `tests/agent-configuration-model-postgres.test.ts`, `tests/agent-configuration-prompts-postgres.test.ts`, `tests/c20-integration-fixture.test.ts`, `tests/local-external-mcp-diagnostic.test.ts`, `tests/preview-openrouter-postgres.test.ts`, and `tests/studio-integration-c20.test.ts`.

  Class (b), documented baseline identities that disappeared/improved in this run: the two stable `tests/external-tools-ui.test.tsx` full-suite identities and `tests/readiness-docker.test.ts` / `kills ignored-stdio descendants after leader exit on timeout` did not fail. None of the five prior submitted-only run-variance failures (three External UI cases, the discovery-process MCP EPIPE/timeout, and the readiness abort-timeout case) recurred. These were not treated as baseline exemptions.

  The task-specific Attempt 2 run of controller, External UI, and all three frozen compatibility suites passed 205/205. Thus all observed full-suite failures match the accepted stable baseline with no C006-owned regression, satisfying the baseline-aware Validation criterion reconciled by Architect Review.

### Deviations

The full repository command exits non-zero due to the exact stable WARN identities enumerated above. Architect Review explicitly reconciled the task gate to baseline-aware no-regression; the Validation checkbox is checked because the Attempt 2 failing set contains no out-of-baseline identity and the focused task packet passes. No tests were weakened or altered beyond the explicitly authorized source loader.

### Assumptions

Attempt 2 followed the latest Architect Review's evidence-only correction requests. The reviewer requested no implementation-source changes unless full-suite classification identified a C006 regression; none was found.

### Unresolved Issues

No unresolved C006-owned issue remains. The known Commerce full-suite WARN identities are documented and classified under `ARCH025-COMMERCE-TEST-001`; Architect acceptance is required before enabling dependent COMMERCE-007.

### Architectural Concerns

None. The controller does not call provider/server validation actions, and execution-kind workflows remain in `ToolEditor`.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 implementation is architecturally conformant on direct source inspection. The accepted C005 -> submitted C006 Commerce delta is bounded to the four authorised task paths (plus generated `tsconfig.tsbuildinfo`): `use-persisted-tool-authoring-controller.ts`, `tool-editor.tsx`, `persisted-tool-authoring-controller.test.tsx`, and the loader-only change in `external-tools-ui.test.tsx`.

The extracted controller preserves the complete common persisted-authoring lifecycle required by R1-R8: selected/base/default restoration; raw persisted buffers and validation flags; canonical `new-tool-authoring-state.ts` freshness; exact Cancel asymmetries; Policy/External/Admin saved-revision convergence; authoring-session overlay/consumption semantics; and the canonical Review identity plus monotonic A→B→A/in-flight fencing. Provider/server validation actions remain in `ToolEditor`; none moved into the controller. The controller surface is sufficient for the consume-only COMMERCE-007..010 contracts without a common-state redesign.

Independent source comparison against accepted COMMERCE-005 found no implementation file outside the authorised C006 set changed. The frozen hashes independently match `d856cac3626605670e08a21826cfcc1a8e6595dcffc764e20d9ef59c2ff78446`, `2245e54996589f7289639bb28c6b364f1726ec291debec390e208a5c304b6c20`, and `267352261520b38eaa9845f93dc09eb8860e75a4010d9da26827c6617bcdcf63`. The `external-tools-ui.test.tsx` delta changes only the deterministic bounded source loader; its behavioural assertions are unchanged.

Acceptance is withheld for evidence/report conformance only.

**A1-R1 — classify the repository-wide suite exactly and close the baseline-aware validation item.**

The Completion Report records a representative full run of 31 failed tests and later variance, but it does not enumerate every failing test identity/collection failure and map each one to `ARCH025-COMMERCE-TEST-001`. Statements that stable identities were present and that task-adjacent files pass in isolation are not sufficient to prove that no new/changed/worsened failure remained in the complete failing set.

For Attempt 2, record the exact failing test identities and collection failures from the submitted-tree full-suite run used for disposition. Classify each as: (a) stable baseline identity with equivalent reason; (b) documented baseline identity that disappeared/improved; or (c) out-of-baseline identity, with its focused/isolated investigation result. Do not add intermittent failures to the durable baseline. If no C006-owned regression is demonstrated, no implementation-source change is required.

The original `npm test exits successfully` wording conflicts with the already accepted durable WARN baseline. This Architect Review reconciles the validation contract to the baseline-aware no-regression rule above. Once the exact identity comparison proves no task-introduced regression, check that Validation item as satisfied and record the evidence; a non-zero repository-wide exit caused only by the accepted baseline does not itself block the task.

**A1-R2 — finish the durable Attempt 2 execution packet.**

The current report records the canonical root, dedicated parent/implementation worktrees, start synchronization, recursive submodule materialisation and Database gitlink, but the final handoff must also record the COMMERCE-005 dependency gate, Attempt 2 claim metadata and durable claim commit, final implementation task-branch head and matching remote head, final parent report head and matching remote head, and clean final status for both worktrees. Use the launcher-prepared packet rather than re-deriving workspace paths.

This correction is evidence-first. Do not modify the controller, ToolEditor, frozen tests, or External loader merely to create a new implementation commit. Make source/test changes only if the exact full-suite classification exposes a C006-owned regression.

### Reviewed Files

- `src/studio/tools/authoring/use-persisted-tool-authoring-controller.ts`
- `src/studio/tools/tool-editor.tsx`
- `tests/persisted-tool-authoring-controller.test.tsx`
- `tests/external-tools-ui.test.tsx`
- frozen `tests/shopify-admin-tools-ui.test.tsx`
- frozen `tests/tool-authoring-screen.test.tsx`
- frozen `tests/new-tool-authoring-state.test.ts`
- `docs/development-baseline.md` (`ARCH025-COMMERCE-TEST-001`)
- this task's Completion Report

### Validation Reviewed

- Direct accepted-C005 -> C006 source comparison: only the four authorised C006 paths changed, excluding generated `tsconfig.tsbuildinfo`.
- Independent SHA-256 verification of all three frozen test assets: exact expected hashes.
- External source-loader diff: loader-only change; existing uniqueness assertion retained.
- Submitted focused evidence: controller + External 105/105; frozen/accepted packet 198/198; additional isolated 182/182; runtime-dependent slice 64/64.
- Submitted `npm run typecheck`: PASS.
- Submitted targeted lint: PASS with only the two documented warnings in untouched Code Response code.
- Submitted `npm run build`: PASS.
- Submitted `git diff --check`: PASS.
- Repository-wide `npm test`: non-green; exact identity classification remains required by A1-R1.

### Architecture Conformance

Implementation conformance: PASS.

Review/validation handoff conformance: CHANGES REQUESTED. The task cannot remain in `review` with a required Validation item intentionally unchecked. After A1-R1 is proven under the durable baseline and A1-R2 is recorded, return the same task to Architect Review.

### Follow-up

Reclaim `ARCH-025-COMMERCE-006` as Attempt 2. Perform the evidence/report corrections above, set the task back to `review`, and STOP. `ARCH-025-COMMERCE-007` remains dependency-gated until this task is architect-accepted Complete.
