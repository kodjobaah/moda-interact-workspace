---
id: ARCH-025-COMMERCE-010
architecture_id: ARCH-025
title: Reduce ToolEditor to final thin persisted-authoring dispatch
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-025-COMMERCE-009
enables: []
created: 2026-10-02
updated: 2026-10-03
---

# Reduce ToolEditor to final thin persisted-authoring dispatch

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Supplementary observations: `docs/architecture/ARCH-025-tool-editor-refactor-observations.md`

Coordinator: `moda_architect`

## Objective

Extract generic revision/read-only/fallback views and reduce `tool-editor.tsx` to the public compatibility shell that selects a revision and dispatches to accepted persisted execution-kind wrappers.

## Context

After COMMERCE-006..009, shared state and all three supported persisted execution-kind workflows have stable owners. The remaining code is revision selection/history, no-revision/create-draft, published read-only/edit-as-new, defensive generic DRAFT editing and final dispatch.

## Scope

Authorised implementation surface:

```text
src/studio/tools/tool-editor.tsx
src/studio/tools/authoring/revision-history.tsx
src/studio/tools/authoring/definition-read-only.tsx
src/studio/tools/authoring/persisted-generic-tool-editor.tsx
tests/tool-editor-dispatch.test.tsx
```

## Out of Scope

Controller/wrapper redesign, new execution kinds, plugin registration framework, publication-rule cleanup, observed-issue fixes or server-action changes.

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

### R1 — final dispatch

Reduce `tool-editor.tsx` to controller composition and small discriminated dispatch using the **accepted COMMERCE-006 selected/base/default-definition state** rather than reimplementing revision selection or default/base restoration in the shell: no selected revision; published revision; Policy DRAFT; External DRAFT; Shopify Admin DRAFT; defensive generic DRAFT fallback. Keep exactly one persisted External DRAFT branch so the accepted source-shape assertion remains meaningful.

### R2 — revision/read-only behaviour

Move `RevisionHistory` and `DefinitionReadOnly` without changing links/text. `ToolEditor` remains the owner that renders RevisionHistory around selected Policy/External/Admin/generic DRAFT wrappers; accepted wrappers from COMMERCE-007..009 are not modified merely to inject history. Preserve the no-selection `Revision history` heading/list and create-draft flow using the controller's exact current default definition. Preserve Edit-as-new from published revision, including existing `createToolDraft` inputs/navigation. Published Policy continues using `PublishedPolicyOperationReadOnly`; other published definitions use generic read-only.

### R3 — generic fallback

Move the existing defensive generic DRAFT editor as-is, including its parse-error retention, save/publish actions and role gating. Preserve its current use of the selected revision's `editVersion`/direct save-publish behaviour rather than retrofitting execution-kind saved-convergence or persisted Test/Review machinery. Do not invent support for another execution kind.

### R4 — no duplicate orchestration

Final ToolEditor must consume the accepted COMMERCE-006 controller and COMMERCE-007..009 wrappers rather than reimplementing their state/workflows.

## Work Items

- [x] Extract revision history/read-only/generic fallback presentation.
- [x] Reduce `tool-editor.tsx` to the final compatibility dispatch shell.
- [x] Add focused dispatch tests.
- [x] Prove all accepted controller/wrapper/source-harness files remain unchanged.

## Interfaces / Contracts

Final repository-internal dispatch/presentation contract. Public compatibility remains the existing `ToolEditor` props/export.

## Dependencies

- `ARCH-025-COMMERCE-009`

## Enables

None

## Acceptance Criteria

- [x] `ToolEditor` public props/import path remain unchanged.
- [x] Revision/no-selection/published/generic fallback behaviour is unchanged.
- [x] Supported persisted DRAFT workflows dispatch to exactly one accepted wrapper each.
- [x] No generic execution-kind plugin framework is introduced.
- [x] All focused frozen and accepted suites pass without weakened expectations; repository-wide run variance is classified in the Completion Report.

## Validation

- [x] Frozen SHA-256 checks print all expected values.
- [x] `npx vitest run tests/tool-editor-dispatch.test.tsx tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/new-tool-authoring-state.test.ts` passes: 5 files, 207 tests.
- [x] Protected diff for the common controller, all three accepted persisted wrappers and `tests/external-tools-ui.test.tsx` is empty.
- [x] `npx vitest run tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/new-tool-authoring-state.test.ts` passes: 4 files, 198 tests.
- [x] `npm test -- --reporter=json` was run on the final tree; it remains nonzero with the documented baseline and six collection gates, plus variable full-suite-only failures that all passed isolated reruns. Exact final totals and identities are recorded below; no task-owned regression was reproduced.
- [x] `npm run typecheck` passes on the final tree.
- [x] Targeted ESLint for all five changed source/test files passes.
- [x] `npm run build` succeeds, including packaging smokes, Prisma generation and Next.js production compilation.
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
- `moda-interact-commerce/src/studio/tools/authoring/revision-history.tsx`
- `moda-interact-commerce/src/studio/tools/authoring/definition-read-only.tsx`
- `moda-interact-commerce/src/studio/tools/authoring/persisted-generic-tool-editor.tsx`
- `moda-interact-commerce/tests/tool-editor-dispatch.test.tsx`

### Work Completed

- Extracted `RevisionHistory`, generic `DefinitionReadOnly`, and the defensive generic DRAFT editor into their dedicated authoring modules. Reduced `ToolEditor` to composition of the accepted controller and the no-selection, published, three persisted-kind, and generic fallback dispatches without changing its public props/export path.
- Kept shell ownership of revision-history rendering around DRAFT wrappers. Preserved the no-selection heading and create-draft default definition, published Policy specialization, generic published read-only view, Edit-as-new action inputs/navigation, generic fallback parsing and role gate, and direct save/publish calls using the selected revision's `editVersion`.
- Added focused dispatch coverage for each persisted wrapper exactly once, no-revision creation, published Policy/read-only behavior, generic read-only fallback, generic parse retention, role gating and direct generic DRAFT save/publish editVersion behavior. The generic future-kind fixture mocks schema acceptance only in the dispatch test so the defensive branch can be exercised without adding a production execution kind or changing production validation.
- The public shell now delegates selected/base/default-definition state to the accepted COMMERCE-006 controller and consumes the accepted COMMERCE-007..009 wrappers. No duplicate controller, plugin framework, new execution kind, or server-action change was introduced.
- Physical isolation: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-COMMERCE-010` on `task/ARCH-025-COMMERCE-010`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-COMMERCE-010` on `task/ARCH-025-COMMERCE-010`. Dedicated worktrees were created; neither shared checkout nor another task worktree was switched/reused.
- Launcher synchronization: parent and implementation task-branch fast-forwards were `not-needed`; `origin/main` was `already-current` in both. Dependency `ARCH-025-COMMERCE-009` was complete and the gate passed. Recursive implementation submodule sync/update passed; Database gitlink was `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3`.
- Claim: Attempt 1 by `copilot` at `2026-10-03T21:36:12Z`; durable parent claim commit `bf8decfe1e7f772b8f1235f6e03ec3ae90d5aee7` was pushed. Implementation started at `59f0ef9f4f3df41ea7804aabb4fa899ad0705028`. Implementation commit `dedef4fa6da07c5b63e4461fec6f288eb3480895` was pushed to `origin/task/ARCH-025-COMMERCE-010`.

### Validation Results

- Focused dispatch/accepted/frozen suite: 5 files, 207 tests passed. Cross-kind suite: 4 files, 198 tests passed. The added generic direct-save test passed and asserts the action receives the selected revision ID and `editVersion`.
- All three required frozen SHA-256 values matched: Shopify Admin UI `d856cac3626605670e08a21826cfcc1a8e6595dcffc764e20d9ef59c2ff78446`; Tool Authoring Screen `2245e54996589f7289639bb28c6b364f1726ec291debec390e208a5c304b6c20`; new-tool authoring state `267352261520b38eaa9845f93dc09eb8860e75a4010d9da26827c6617bcdcf63`.
- Protected diff check was empty for `use-persisted-tool-authoring-controller.ts`, the Policy, External HTTP and Shopify Admin persisted wrappers, and `tests/external-tools-ui.test.tsx`. Implementation changes were confined to the five authorized files. `git diff --check` passed.
- Runtime/toolchain: Node `v24.19.0`, npm `11.17.0`; repository scripts are `test: vitest run`, `typecheck: next typegen && tsc --noEmit`, `lint: eslint .`, and the declared packaging/Prisma/Next build pipeline.
- `npm run typecheck`: passed on the final tree. Targeted ESLint passed for all five changed source/test files.
- `npm run build`: passed on the final tree. Manuals package/smoke, code-runtime package/smoke, Prisma Client generation, Next.js webpack production build, type generation, static page generation, traces and finalization all succeeded. Packaged QuickJS SHA-256 `d4c9375f2b1ca4dc95f72c8aa2982a7a9951ac8011490d79c6582df732b4bbd9`; `helpers-v2.js` SHA-256 `83fe8b710c646680781e605baa64f77ef215cea9bd7aa7df4133afd358c9c31a`. Next emitted the existing Nunjucks critical-dependency warnings.
- Final `npm test -- --reporter=json`: nonzero; 42 failing files, 40 failing tests, 1,368 passing tests and 9 skipped tests. The 30 failing test identities outside the run-only set match the stable failing identities in `ARCH025-COMMERCE-TEST-001`; six collection failures match its documented environment/invocation gates (`COMMERCE_TEST_DATABASE_URL`, disposable C20 targets, and explicit local External MCP diagnostic invocation).
- The final full run's 10 additional test failures were: five `tests/code-response-processor.test.ts` cases; three `tests/external-tools-ui.test.tsx` cases; one `tests/feature-configuration-screen.test.tsx` case; and one `tests/shopify-admin-tools-ui.test.tsx` case. All four files passed together in isolation, 157/157 tests. An earlier full-suite run in this attempt showed a QuickJS supervisor proof failure and one External UI timeout; the two affected files passed together in isolation, 110/110 tests. These changing full-suite-only failures are not treated as baseline exemptions; none reproduced in isolated runs or the required focused/cross-kind suites. No failure was found in C010-owned tests or implementation.
- `git diff --check` passed. Implementation `HEAD` and `origin/task/ARCH-025-COMMERCE-010` both equal `dedef4fa6da07c5b63e4461fec6f288eb3480895`; implementation worktree was clean and its Database gitlink remained unchanged.

### Deviations

- Repository-wide `npm test` did not return green. Its stable failures match `ARCH025-COMMERCE-TEST-001`; collection gates also match that baseline. Multiple full-suite runs produced different additional failures, all of which passed when their affected files were rerun in isolation. This instability remains visible for Architect review; the task-specific dispatch/frozen/accepted checks, typecheck, lint and production build are green.

### Assumptions

- No task-owned regression was reproduced. The generic fallback still cannot represent an additional execution kind under the canonical three-kind schema; the test mocks schema acceptance only to verify the existing defensive branch's generic action wiring. Production validation remains unchanged.

### Unresolved Issues

- The full-suite-only failures described above are outside the five changed files; their identities vary between full runs and their affected suites pass in isolation. Architect review should assess the existing repository suite instability rather than treating those transient failures as C010 baseline exemptions.

### Architectural Concerns

None

## Architect Review

### Review Status

Accepted — Attempt 1

### Review Notes

- The final ToolEditor refactor is a bounded move-only extraction. Direct comparison with architect-accepted COMMERCE-009 shows that, excluding generated `tsconfig.tsbuildinfo`, the Commerce delta is exactly the five authorised C010 paths.
- `RevisionHistory`, generic `DefinitionReadOnly`, and the defensive generic DRAFT editor preserve the accepted C009 implementation semantics; `ToolEditor` retains its public props/export and is reduced to controller composition plus no-selection, published, Policy, External HTTP, Shopify Admin and generic fallback dispatch.
- The common persisted-authoring controller, all three accepted persisted execution-kind wrappers and the accepted `tests/external-tools-ui.test.tsx` harness are byte-identical to COMMERCE-009. All three frozen Tool-authoring test hashes remain exact.
- Repository-wide validation remains non-green only under the documented `ARCH025-COMMERCE-TEST-001` baseline plus changing full-suite-only failures that passed their affected-file isolated reruns. Those transient identities are not added to the baseline and no C010-owned regression was reproduced.
- Implementation `dedef4fa6da07c5b63e4461fec6f288eb3480895` and parent report `b63f66148d28c513f0e77a15971ecb1eaea729b5` are the submitted review heads; the report records dedicated launcher-resolved worktrees, synchronization, recursive submodule preparation, dependency gating and clean implementation remote alignment.

### Reviewed Files

- `moda-interact-commerce/src/studio/tools/tool-editor.tsx`
- `moda-interact-commerce/src/studio/tools/authoring/revision-history.tsx`
- `moda-interact-commerce/src/studio/tools/authoring/definition-read-only.tsx`
- `moda-interact-commerce/src/studio/tools/authoring/persisted-generic-tool-editor.tsx`
- `moda-interact-commerce/tests/tool-editor-dispatch.test.tsx`
- Protected controller/wrappers and frozen regression assets by direct C009/C010 hash/diff comparison.

### Validation Reviewed

- Focused dispatch/accepted/frozen suite: 207/207 passed.
- Cross-kind suite: 198/198 passed.
- Frozen SHA-256 values: exact.
- Protected owner/source-harness diff: empty.
- `npm run typecheck`: passed.
- Targeted ESLint: passed.
- `npm run build`: passed, including manuals/code-runtime packaging smokes, Prisma generation and Next.js production build.
- `npm test -- --reporter=json`: stable failures/collection gates classified against `ARCH025-COMMERCE-TEST-001`; ten changing full-run-only failures passed their affected-file isolated rerun (157/157), and earlier run-only QuickJS/External variance passed its two-file isolated rerun (110/110).
- `git diff --check`: passed.

### Architecture Conformance

Conformant. C010 completes the ToolEditor persisted-authoring structural tranche without changing product behaviour, server contracts, publication semantics, execution-kind contracts, Test/revision freshness or canonical specialised owners. No generic execution-kind framework or duplicate orchestration was introduced.

### Follow-up

None for C010. This is the final ARCH-025 implementation task. The parent architecture explicitly declares separate `moda_system_test` validation not applicable to this structural maintainability initiative, so acceptance completes the architecture-wide implementation graph.
