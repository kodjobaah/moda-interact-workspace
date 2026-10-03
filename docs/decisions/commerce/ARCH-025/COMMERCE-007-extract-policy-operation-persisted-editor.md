---
id: ARCH-025-COMMERCE-007
architecture_id: ARCH-025
title: Extract persisted Policy Operation Tool editor
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
claimed_at: 2026-10-03T15:35:16Z
attempt: 1
depends_on:
  - ARCH-025-COMMERCE-006
enables:
  - ARCH-025-COMMERCE-008
created: 2026-10-02
updated: 2026-10-03
---

# Extract persisted Policy Operation Tool editor

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Supplementary observations: `docs/architecture/ARCH-025-tool-editor-refactor-observations.md`

Coordinator: `moda_architect`

## Objective

Extract the persisted Policy Operation DRAFT workflow behind a focused wrapper that consumes the accepted COMMERCE-006 controller and existing Policy editor owners.

## Context

Policy Operation already has a specialised `PolicyOperationEditor`; ToolEditor still owns its candidate construction, immutable binding checks, section validity/Test gating, save convergence and publish flow. This is the lowest-risk execution-kind branch to move first.

## Scope

Authorised implementation surface:

```text
src/studio/tools/tool-editor.tsx
src/studio/tools/authoring/persisted-policy-operation-tool-editor.tsx
tests/persisted-policy-operation-tool-editor.test.tsx
```

## Out of Scope

Common controller changes, External/Admin extraction, Policy descriptor/mapping implementation changes, server-action changes or Policy behaviour redesign.

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

Consume the accepted COMMERCE-006 controller. Do not add common state/actions to it. If something is missing, stop and return to `moda_architect`.

### R2 — immutable Policy identity/binding

Preserve immutable MCP name, operation and operationVersion checks before save and against the returned saved revision. Preserve descriptor-driven mapping ownership in `PolicyOperationEditor`.

### R3 — Policy section/Test/save/publish gates

Preserve current owning-section validation, current Test requirement, CAS `expectedEditVersion`, exact save reason, returned identity verification, saved editVersion convergence, dirty clearing/editor remount/authoring-session consumption, SUPER_ADMIN publication, 1..1000 trimmed user reason and current-Test publication gate.

### R4 — no duplicate Policy implementation

The wrapper composes `PolicyOperationEditor` and existing server actions/state helpers; it must not duplicate descriptor, mapping or live-Test implementations.

### R5 — RevisionHistory remains shell-owned until COMMERCE-010

Do not import `RevisionHistory` back from `tool-editor.tsx` (which would create a wrapper/shell cycle) and do not duplicate it inside the Policy wrapper. During COMMERCE-007, `ToolEditor` continues to render the existing `RevisionHistory` immediately around the extracted Policy DRAFT wrapper. `RevisionHistory` itself is extracted only by COMMERCE-010.

## Work Items

- [x] Extract Policy DRAFT candidate/build/save/publish orchestration.
- [x] Keep published Policy read-only handling outside this wrapper.
- [x] Keep `RevisionHistory` rendered by the ToolEditor shell; do not duplicate or reverse-import it into the wrapper.
- [x] Add focused wrapper tests where frozen suites do not already pinpoint the boundary.
- [x] Prove common controller and accepted COMMERCE-006 External source harness remain unchanged.

## Interfaces / Contracts

Repository-internal persisted Policy DRAFT wrapper over the accepted controller and existing Policy editor/server actions.

## Dependencies

- `ARCH-025-COMMERCE-006`

## Enables

- `ARCH-025-COMMERCE-008`

## Acceptance Criteria

- [x] Policy DRAFT rendering/validation/Test/save/publish behaviour is unchanged.
- [x] Immutable Policy binding and returned-save identity verification are preserved.
- [x] Common controller is unchanged.
- [x] Accepted COMMERCE-006 External suite and frozen suites pass.

## Validation

- [x] All three frozen SHA-256 values match their specified hashes.
- [x] The Policy wrapper test and frozen Shopify Admin UI test pass (included in the final combined run below).
- [x] The diff for the accepted C006 controller and External suite source harness is empty.
- [x] The wrapper and all four accepted/frozen compatibility suites pass: 5 files, 199 tests.
- [x] `npm test` produced no task-introduced regression; full-suite variance and baseline classification are recorded below.
- [x] `npm run typecheck` passes after build-generated Prisma Client is present.
- [x] Targeted ESLint on changed source/test files passes without warnings.
- [x] `npm run build` succeeds.
- [x] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Commerce task.

## Implementation Notes

None

## Completion Report

### Status

Submitted for Architect review. Attempt 1; task status set to `review`.

### Files Changed

`src/studio/tools/tool-editor.tsx`

`src/studio/tools/authoring/persisted-policy-operation-tool-editor.tsx` (new)

`tests/persisted-policy-operation-tool-editor.test.tsx` (new)

### Work Completed

Moved persisted Policy Operation DRAFT candidate construction, immutable identity and operation/version binding checks, section/Test save gates, CAS save action, returned revision verification/convergence, and SUPER_ADMIN publication gating into `PersistedPolicyOperationToolEditor`.

`ToolEditor` still creates exactly one accepted COMMERCE-006 controller instance and passes it to the wrapper. It renders `RevisionHistory` immediately before the wrapper and retains published Policy read-only handling and all other dispatch paths. `PolicyOperationEditor` remains the descriptor/mapping/live-Test owner. No common controller, External harness, server action, or frozen test was changed.

Added direct wrapper coverage for canonical candidate construction, save reason and expected editVersion, returned revision convergence, and immutable Policy identity. Implementation commit `a079b90861d9f507e532257e591baf78e4e48932` is pushed to `origin/task/ARCH-025-COMMERCE-007`.

### Validation Results

Focused wrapper and compatibility validation passed: `npx vitest run tests/persisted-policy-operation-tool-editor.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/external-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/new-tool-authoring-state.test.ts`; 5 files / 199 tests.

Frozen hashes matched: Shopify Admin UI `d856cac3626605670e08a21826cfcc1a8e6595dcffc764e20d9ef59c2ff78446`; Tool Authoring Screen `2245e54996589f7289639bb28c6b364f1726ec291debec390e208a5c304b6c20`; New Tool Authoring State `267352261520b38eaa9845f93dc09eb8860e75a4010d9da26827c6617bcdcf63`. The accepted C006 controller and External suite source-harness diff is empty.

Targeted ESLint passed without warnings. `npm run build` passed, including Prisma generation and Next production build; Next emitted only the existing Nunjucks dynamic-dependency warning. `npm run typecheck` passed after Prisma Client generation. `git diff --check` passed.

Full-suite evidence was variable. `npm test` reported 23 failed files / 141 passed files / 5 skipped files and 39 failed tests / 1,359 passed / 9 skipped. A structured full-suite rerun reported 32 failed tests / 1,366 passed / 9 pending and six collection failures. All six collection failures matched `ARCH025-COMMERCE-TEST-001`; exact structured-run test comparison matched its stable identities except the previously submitted-only `tests/readiness-docker.test.ts` case `kills ignored-stdio descendants after leader exit on abort`. That case passed when its owning file was rerun in isolation (10/10). The two documented External UI failures were absent in the structured run. No C007-owned failure was observed.

Launcher evidence: dependency `ARCH-025-COMMERCE-006` was `complete`; dependency gate passed. Attempt 1 was claimed by `copilot` at `2026-10-03T15:35:16Z`; durable parent claim commit `a237c451fba1a6dc4873d80a07d4018874920c94` was committed and pushed. Parent and implementation task branches required no task-branch fast-forward and already contained `origin/main`. Recursive submodule sync/update passed; Database remained pinned at `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3`. Implementation local/remote HEADs matched at `a079b90861d9f507e532257e591baf78e4e48932` before report submission. Parent report is committed/pushed on the mirrored task branch; both task worktrees were clean after publication.

### Deviations

No implementation deviation. The full repository suite remains variable and non-green on documented baseline conditions; the one observed non-baseline readiness abort-timeout identity passed when isolated.

### Assumptions

No additional assumptions beyond the move-only extraction contract and accepted COMMERCE-006 controller.

### Unresolved Issues

No C007-owned unresolved issue. `ARCH025-COMMERCE-TEST-001` remains applicable to documented full-suite and collection failures.

### Architectural Concerns

None. The wrapper consumes the accepted common controller and existing Policy editor/action owners, while the ToolEditor shell retains revision history and published dispatch.

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
