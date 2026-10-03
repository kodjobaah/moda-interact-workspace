---
id: ARCH-025-COMMERCE-009
architecture_id: ARCH-025
title: Extract persisted Shopify Admin Tool editor
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
claimed_at: 2026-10-03T19:39:36Z
attempt: 1
depends_on:
  - ARCH-025-COMMERCE-008
enables:
  - ARCH-025-COMMERCE-010
created: 2026-10-02
updated: 2026-10-03
---

# Extract persisted Shopify Admin Tool editor

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Supplementary observations: `docs/architecture/ARCH-025-tool-editor-refactor-observations.md`

Coordinator: `moda_architect`

## Objective

Extract the persisted Shopify Admin GraphQL DRAFT workflow into a focused wrapper that preserves compiler/result-contract freshness, Explore handoff, Test, save and publish behaviour.

## Context

The Admin branch has distinct variable mapping and derived result-contract semantics. It must move without conflating mapping freshness with query/result identity or changing the existing server-authoritative publication gate.

## Scope

Authorised implementation surface:

```text
src/studio/tools/tool-editor.tsx
src/studio/tools/authoring/persisted-shopify-admin-tool-editor.tsx
tests/persisted-shopify-admin-tool-editor.test.tsx
```

## Out of Scope

Common controller changes, Shopify Admin compiler/editor redesign, Explore workflow redesign, server-action changes, publication-rule cleanup or observed-issue fixes.

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

### R1 — consume-only controller

Consume the accepted COMMERCE-006 controller without expanding it.

### R2 — Admin request/result freshness

Preserve the current distinction: document, operationName, apiVersion, schemaHash or resultPath changes stale `adminResultContractFresh`; variable/literal mapping-only changes do **not** stale the already-derived result contract. Preserve `adminMappingValid` independently.

### R3 — Explore Shopify handoff

Preserve the exact existing `onOpenAdminExplore` existing-draft authoring-session payload: tool/revision identity, current candidate, Result Template metadata and raw editor buffers (`section`, input/response/result-schema/result-path/literal text). No persistence occurs merely by opening Explore.

### R4 — Test/save/publish convergence

Preserve current Test requirement before save, result-contract/mapping gates, CAS editVersion, returned saved definition/editVersion restoration, dirty clearing, `adminValidated` reset, editor remount and authoring-session consumption. Preserve current publish action/reason/client gates and server-authoritative `LIVE_TEST_REQUIRED` behaviour; do not introduce a new client Test publication gate in this structural task.

### R5 — Result Template/Review

Preserve output-schema fallback, Result Template metadata/validation and Review candidate/presentation exactly.

### R6 — RevisionHistory remains shell-owned until COMMERCE-010

Keep `RevisionHistory` rendered by `ToolEditor`; do not duplicate it in the Admin wrapper or import it back from the shell. COMMERCE-010 owns the eventual `revision-history.tsx` extraction.

## Work Items

- [x] Extract Shopify Admin persisted DRAFT wrapper.
- [x] Keep RevisionHistory shell-owned until COMMERCE-010.
- [x] Keep `ShopifyAdminEditor`, `ShopifyAdminResponseEditor` and `ShopifyAdminTestTab` canonical.
- [x] Add focused wrapper tests where useful.
- [x] Prove controller, Policy/External wrappers and frozen suites remain unchanged.

## Interfaces / Contracts

Repository-internal persisted Shopify Admin DRAFT wrapper consuming the common controller and existing Admin editor/compiler/server actions.

## Dependencies

- `ARCH-025-COMMERCE-008`

## Enables

- `ARCH-025-COMMERCE-010`

## Acceptance Criteria

- [x] Admin mapping/result-contract freshness semantics are unchanged.
- [x] Explore authoring-session round trip is unchanged.
- [x] Save uses returned editVersion and existing convergence semantics.
- [x] Existing client/server publication behaviour is unchanged.
- [x] Prior accepted modules/tests remain unchanged.

## Validation

- [x] Frozen SHA-256 checks print all three expected hashes.
- [x] `npx vitest run tests/persisted-shopify-admin-tool-editor.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx` passes: 3 files, 78 tests.
- [x] Protected diff check is empty for the common controller, Policy/External wrappers and frozen External UI test.
- [x] `npx vitest run tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/new-tool-authoring-state.test.ts` passes: 4 files, 198 tests.
- [x] `npm test` was run twice; results and non-task failures are classified in the Completion Report. The structured rerun contains the durable baseline identities plus one separately reproduced, unchanged readiness-test timing failure; first-run-only variance is recorded as unresolved.
- [x] `npm run typecheck` passes.
- [x] Targeted ESLint for the three changed source/test files passes.
- [x] `npm run build` succeeds, including both packaging smokes, Prisma generation and the full Next.js production build.
- [x] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Commerce task.

## Implementation Notes

None

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-commerce/src/studio/tools/tool-editor.tsx`
- `moda-interact-commerce/src/studio/tools/authoring/persisted-shopify-admin-tool-editor.tsx`
- `moda-interact-commerce/tests/persisted-shopify-admin-tool-editor.test.tsx`

### Work Completed

- Extracted the persisted Shopify Admin GraphQL DRAFT workflow into `PersistedShopifyAdminToolEditor`; kept the public `ToolEditor` boundary, persisted-kind dispatch and `RevisionHistory` shell-owned.
- Kept the common authoring controller, Policy/External wrappers, specialized Shopify Admin editors, Explore workflow and server actions unchanged. The wrapper test covers the extracted surface; the focused and cross-kind suites exercise the preserved authoring behavior.
- Preserved independent result-contract freshness and mapping validity; the exact Explore authoring-session handoff; Test/result-contract/mapping save gates; CAS/editVersion save convergence; admin validation reset, editor remount and session consumption; and existing client/server publication behavior.
- Physical isolation: canonical workspace root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-COMMERCE-009`; Commerce implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-COMMERCE-009`. Parent and implementation used separate worktrees on their mirrored `task/ARCH-025-COMMERCE-009` branches; implementation edits and validation ran in the Commerce worktree, not the canonical checkout or parent worktree.
- Launcher synchronization: parent and implementation task-branch fast-forwards were `not-needed`; both `origin/main` refs were `already-current`. Dependency `ARCH-025-COMMERCE-008` was complete and its gate passed. Recursive implementation submodule sync/init/update passed; Database remained at gitlink `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3`.
- Claim: Attempt 1, executor `copilot`, claimed `2026-10-03T19:39:36Z`; durable parent claim commit `f3abe144737a154bb4249417d76ce8e01e18f0d9` was pushed. Implementation started at `5be043d0761288ff8d94d01f7c21f4ac5d482c98`; implementation commit `c5b4b83d2d08943aa870fea546df32718fac8e34` was pushed to the mirrored task branch. Final implementation verification found a clean worktree and local `HEAD` equal to `origin/task/ARCH-025-COMMERCE-009`.

### Validation Results

- Frozen SHA-256 checks matched the required values for `tests/shopify-admin-tools-ui.test.tsx`, `tests/tool-authoring-screen.test.tsx` and `tests/new-tool-authoring-state.test.ts`.
- Protected diff against `origin/main` was empty for the common controller, Policy wrapper, External wrapper and `tests/external-tools-ui.test.tsx`; the implementation diff is limited to the three authorized C009 files. `git diff --check` passed.
- Focused wrapper/Admin suite: 3 files, 78 tests passed. Cross-kind compatibility suite: 4 files, 198 tests passed.
- `npm run typecheck` passed under Node `v24.19.0` / npm `11.17.0`; `package-lock.json` SHA-256 is `d8ebcf87bcd1ce0c9d2b62b88784abf359697e9149d97eadd04f97af04469d35`.
- Targeted ESLint passed for `tool-editor.tsx`, `persisted-shopify-admin-tool-editor.tsx` and its test.
- `npm run build` passed: manuals package/smoke, code-runtime package/smoke, Prisma Client generation and Next.js webpack production build, including type generation, static pages, traces and finalization. Packaged QuickJS SHA-256: `d4c9375f2b1ca4dc95f72c8aa2982a7a9951ac8011490d79c6582df732b4bbd9`; `helpers-v2.js` SHA-256: `83fe8b710c646680781e605baa64f77ef215cea9bd7aa7df4133afd358c9c31a`. Next emitted existing Nunjucks critical-dependency warnings; build completed successfully.
- First `npm test`: exit non-zero, 46 failed / 1,353 passed / 9 skipped tests (27 failed / 138 passed / 5 skipped files). The available console capture exposed four 15-second `tests/tool-authoring-screen.test.tsx` timeouts and one `externalPreview.validate` call-count assertion, in addition to a frozen StudioWorkspace failure; the capture did not preserve all failure identities.
- Structured full-suite rerun with Vitest JSON reporter: 31 failed / 1,368 passed / 9 skipped tests out of 1,408, plus six collection failures. The six collection gates match `ARCH025-COMMERCE-TEST-001` (`COMMERCE_TEST_DATABASE_URL`, disposable C20 targets, and the explicit local External MCP diagnostic invocation). The failed tests matched documented baseline identities except the readiness abort-path test described below. The first-run `tool-authoring-screen` failures were not reproduced: that frozen file passed alone, 34/34 tests.
- `tests/readiness-docker.test.ts` also failed alone, 2/10 tests: both “kills ignored-stdio descendants after leader exit on timeout” and the abort-path variant fail at the pre-cancellation assertion because the child readiness marker is not observed. The abort-path identity is not the baseline’s timeout identity, so it is recorded as an additional environment/timing failure, not baseline-exempted. The test and readiness implementation are unchanged from `origin/main` and outside C009 scope.

### Deviations

- The initial full-suite run reported 15 more failures than the structured rerun. Five initially visible `tool-authoring-screen` failures passed when rerun alone; the first run’s output did not retain enough detail to identify/classify its other run-only failures. The complete structured rerun returned to the documented baseline failure set plus the separately reproduced readiness abort timing failure. This non-deterministic full-suite variance is reported for Architect assessment; no C009-owned failure was reproduced.

### Assumptions

- The extracted Admin workflow is validated by focused wrapper/Admin coverage, cross-kind coverage, unchanged frozen hashes, protected-file checks, typecheck, targeted lint and a successful production build. Full-suite status remains non-zero because of the documented Commerce baseline and an unrelated child-process readiness timing failure.

### Unresolved Issues

- No C009 implementation regression was identified. Architect review should assess the unclassified first-run-only full-suite variance and the unchanged readiness abort-path timing failure; neither is owned by this task.

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
