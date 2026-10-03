---
id: ARCH-025-COMMERCE-008
architecture_id: ARCH-025
title: Extract persisted External HTTP Tool editor
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
claimed_at: 2026-10-03T17:06:45Z
attempt: 1
depends_on:
  - ARCH-025-COMMERCE-007
enables:
  - ARCH-025-COMMERCE-009
created: 2026-10-02
updated: 2026-10-03
---

# Extract persisted External HTTP Tool editor

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Supplementary observations: `docs/architecture/ARCH-025-tool-editor-refactor-observations.md`

Coordinator: `moda_architect`

## Objective

Extract the persisted External HTTP DRAFT workflow into a focused wrapper while preserving request/response validation, live-Test, Result Template, Review and publication semantics.

## Context

External HTTP is the largest execution-kind branch. It owns authorised connection availability, request/response authoring actions, local raw response-processing/result-schema buffers, live Test, authoritative Review validation, save convergence and publication presentation.

## Scope

Authorised implementation surface:

```text
src/studio/tools/tool-editor.tsx
src/studio/tools/authoring/persisted-external-http-tool-editor.tsx
tests/persisted-external-http-tool-editor.test.tsx
```

## Out of Scope

Common controller changes, ExternalHttpEditor/response implementation redesign, provider protocol changes, publication-rule cleanup or observed-issue fixes.

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

### R2 — External provider/authoring boundary

Preserve `ExternalHttpEditor`, preview request, request validation, response observation, response validation and live-Test action ownership exactly. Preserve authorised-port unavailable presentation and connectionRevisionId pinning. Do not add/remove provider calls.

### R3 — External revisions/Test/Result Template

Preserve Request/Response/Result Template revision advancement and STALE transitions, local raw response-processing/result-schema retention, Result Template metadata and validation, and current live-Test requirement before save. Preserve the current no-port asymmetry recorded as observation O9: when the authorised External port is unavailable, editing the fallback raw Input Schema marks dirty and invalidates External validation but does **not** explicitly advance the common Request revision. Do not normalise that path during extraction.

### R4 — Review validation/save convergence

Preserve Review action-key generation/in-flight fencing. On save, preserve `candidateWasValidated` capture and retain `externalValidated` only when the returned saved definition is canonically identical to the submitted candidate. Preserve the existing post-save asymmetries documented in the observations file; do not normalize them.

### R5 — publication

Preserve current SUPER_ADMIN gate, dirty/definition/authoritative-validation/reason checks and server-authoritative `LIVE_TEST_REQUIRED` behaviour exactly. Do not add a new client Test publication gate in this structural task.

### R6 — shell-owned RevisionHistory and source-shape branch

Keep `RevisionHistory` rendered by `ToolEditor` until COMMERCE-010; do not duplicate it or import it back from the shell into the wrapper. Keep exactly one source-shape branch matching the accepted persisted External DRAFT uniqueness assertion (`selected?.status === "DRAFT"` plus `definition.execution.kind === "EXTERNAL_HTTP"`) in the bounded ToolEditor module set after extraction.

## Work Items

- [x] Extract External persisted DRAFT wrapper and server-action wiring.
- [x] Keep RevisionHistory and the single persisted-External dispatch condition shell-owned until COMMERCE-010.
- [x] Keep existing specialised External editor/result/review components canonical.
- [x] Use existing persisted External UI and controller tests for save/validation convergence; a separate wrapper-only test was not needed.
- [x] Prove controller, Policy wrapper and accepted External source harness remain unchanged.

## Interfaces / Contracts

Repository-internal persisted External HTTP DRAFT wrapper consuming the common controller and existing External authoring ports/actions.

## Dependencies

- `ARCH-025-COMMERCE-007`

## Enables

- `ARCH-025-COMMERCE-009`

## Acceptance Criteria

- [x] External Request/Response/Test/Result Template/Review behaviour is unchanged.
- [x] One provider/action call pattern and stale-validation suppression are unchanged.
- [x] Returned-candidate equality controls validation retention exactly as today.
- [x] Existing server-authoritative publication rejection behaviour is preserved.
- [x] Prior accepted modules/tests remain unchanged.

## Validation

- [x] Frozen SHA-256 hashes print all expected values.
- [x] `npx vitest run tests/persisted-external-http-tool-editor.test.tsx tests/external-tools-ui.test.tsx`: 98 passed in the existing External UI suite; the named wrapper-only test file does not exist and Vitest ignored that path. Existing tests cover persisted-DRAFT save/duplicate-save, validation, and server-authoritative publication rejection.
- [x] Protected diff check is empty for the common controller, Policy wrapper and three frozen tests.
- [x] `npx vitest run tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/new-tool-authoring-state.test.tsx`: 198 passed.
- [ ] `npm test`: non-zero; 1,315 passed, 74 failed and 9 skipped across 169 files. A focused rerun reproduced six failures in `tests/studio-workspace.test.tsx`; all six match the frozen failures documented by `ARCH025-COMMERCE-TEST-001`. `tests/tool-authoring-screen.test.tsx` passed 41/41 in that rerun; two External HTTP timeouts reported in the full run were not reproduced. The full-run aggregate did not enumerate all failure identities, so repository-wide status remains unresolved for Architect review.
- [x] `npm run typecheck` passed after Prisma client generation.
- [x] Targeted ESLint for `tool-editor.tsx` and `persisted-external-http-tool-editor.tsx` passed.
- [ ] `npm run build`: blocked before Next.js build by unchanged packaged-runtime smoke `scripts/code-runtime-packaged-smoke.mjs`, which reported `packaged v2 helper namespace is mutable`. No matching baseline entry was found; this unrelated failure remains unresolved for Architect review.
- [x] `git diff --check` passed.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Commerce task.

## Implementation Notes

None

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-commerce/src/studio/tools/tool-editor.tsx`
- `moda-interact-commerce/src/studio/tools/authoring/persisted-external-http-tool-editor.tsx`

### Work Completed

- Extracted the persisted External HTTP DRAFT workflow and its existing server-action wiring into `PersistedExternalHttpToolEditor` without changing the common controller or specialised External editor.
- Kept the single accepted persisted External DRAFT source-shape dispatch condition and `RevisionHistory` rendering in the `ToolEditor` shell.
- Preserved the common controller, Policy wrapper, specialised External editor, provider/action call ownership, no-port Request behavior, returned-candidate equality check, Review validation fencing and publication behavior.
- No wrapper-only test file was added: the existing External UI suite directly exercises the persisted-DRAFT authoring path, and accepted controller tests cover save convergence and validation fencing.
- Physical worktree isolation: canonical workspace root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-COMMERCE-008` on `task/ARCH-025-COMMERCE-008`; Commerce implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-COMMERCE-008` on `task/ARCH-025-COMMERCE-008`. Shared workspace checkout switched/mutated for task work: no. Shared implementation checkout switched/mutated for task work: no. Another task worktree reused: no.
- Start synchronization: parent and implementation task-branch fast-forwards were `not-needed`; parent and implementation `origin/main` were `already-current`. Dependency `ARCH-025-COMMERCE-007` was `complete` and the gate passed. Recursive implementation submodule sync and init/update passed; Database was initialized at recorded gitlink `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3`.
- Claim: Attempt 1 by `copilot` at `2026-10-03T17:06:45Z`; durable parent claim commit `defc9dda87d00fc4344814b5faed906c91cac7a3` was pushed. Implementation commit `c96248298d3c62be7e5a1ab92f55a063b1c41b94` was pushed on `task/ARCH-025-COMMERCE-008`; the local branch tracks and matches its origin task ref. The parent report is published on the mirrored task branch; final verification confirmed both worktrees clean and each local task branch equal to its corresponding `origin/task/ARCH-025-COMMERCE-008` ref.

### Validation Results

- Frozen SHA-256 checks: all three expected hashes matched for `tests/shopify-admin-tools-ui.test.tsx`, `tests/tool-authoring-screen.test.tsx` and `tests/new-tool-authoring-state.test.ts`.
- Protected diff check: empty for the common controller, Policy wrapper and three frozen tests.
- `npx vitest run tests/persisted-external-http-tool-editor.test.tsx tests/external-tools-ui.test.tsx`: passed; 98 tests.
- `npx vitest run tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/new-tool-authoring-state.test.ts`: passed; 198 tests.
- `npm test`: non-zero; summary reported 1,315 passed, 74 failed and 9 skipped across 169 files. Named failures were `tests/studio-workspace.test.tsx` (`retains editor input after stale CAS`, unable to find the Shopify Admin `Save draft` button) and two 15-second timeouts in `tests/tool-authoring-screen.test.tsx` new-tool local External HTTP cases. These are outside the moved persisted External wrapper; the frozen `tool-authoring-screen` hash and targeted test set passed. The full-suite output did not enumerate all failures represented by its aggregate count.
- `npm run typecheck`: passed after the build's Prisma client generation.
- `npx eslint src/studio/tools/tool-editor.tsx src/studio/tools/authoring/persisted-external-http-tool-editor.tsx`: passed.
- `npm run build`: blocked before Next.js build by the unchanged packaged-runtime smoke, `scripts/code-runtime-packaged-smoke.mjs`, which reported `packaged v2 helper namespace is mutable`. This code/runtime path is outside task scope and no matching documented baseline entry was found; the failure is reported as unresolved, not treated as passing.
- `git diff --check`: passed.

### Deviations

The requested production build did not complete because the unchanged packaged code-runtime smoke failed. No out-of-scope runtime or smoke changes were made. Repository-wide test failures are recorded above; the focused persisted External and neighboring authoring suites passed, and the only focused `studio-workspace` failures match the documented frozen baseline.

### Assumptions

The wrapper is only reached from the shell's persisted External DRAFT dispatch; its guard is defensive and does not change the dispatch contract.

### Unresolved Issues

Architect review should determine disposition of the unrelated packaged code-runtime smoke failure and the repository-wide test failures before acceptance.

### Architectural Concerns

None. No cross-repository contract or architecture changes were required.

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
