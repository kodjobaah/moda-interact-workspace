---
id: ARCH-025-COMMERCE-002
architecture_id: ARCH-025
title: Extract immutable Release Composer
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
  - ARCH-025-COMMERCE-001
enables:
  - ARCH-025-COMMERCE-003
created: 2026-10-02
updated: 2026-10-03
---

# Extract immutable Release Composer

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract immutable Release composition and response-contract validation into a dedicated module without changing validation freshness, role gating, creation or navigation semantics.

## Context

`ReleaseComposer` is the largest domain-specific view in StudioWorkspace and owns a complete local state/validation lifecycle distinct from global workspace orchestration. COMMERCE-001 already establishes the global command/navigation contract it consumes.

## Scope

Authorised implementation surface:

```text
components/studio-workspace.tsx
components/studio-workspace/release-composer.tsx
tests/release-composer.test.tsx
```

## Out of Scope

Workspace-controller changes, Release Detail extraction, Shop views, generic page-router extraction, server-action or contract changes.

## Requirements

### Common ARCH-025 StudioWorkspace invariants

- This is a **move-only structural refactor**. Do not change Studio product behaviour, server-action signatures/authorization, persistence semantics, Tool authoring, Agent Configuration, Discovery, Test Conversations/Preview or Shop execution contracts.
- Preserve `StudioWorkspace` and the `StudioPage` type at `components/studio-workspace.tsx`. Existing production callers/browser-evidence fixtures do not migrate.
- Preserve route identity as `page:detailId:revisionId:authoringSessionId`, while the page/detail load effect continues to trigger only from `page`, `detailId` and `revisionId`; changing only `authoringSessionId` must not add a Studio data load.
- Preserve one-time `initialResult`/`initialDetail` hydration suppression through the hydrated route identity and monotonic `loadToken` stale-result rejection.
- Preserve current page-load/provider cardinality/order: Tool list/detail, Explore schema, Release list/detail and Shop list/detail calls must not be added, removed, merged or reordered as incidental cleanup. Agent Configuration still performs no Studio list/detail server action and sets the bounded local loaded state.
- Preserve write single-flight through the current pending ref/token semantics. A second write is not admitted while one is pending; an `unknown` outcome stores the original operation ID, label, run callback, admitted content revision and optional success callback for reconciliation.
- Preserve the current operation-ID format (`c` + base36 `Date.now()` + 18 hex-like UUID characters with hyphens removed) everywhere it is used, including Release edit-as-new handoff.
- Preserve content-revision dirty fencing: `setDirty(true)` increments the content revision; a successful command clears dirty only when the submitted revision still equals the current revision.
- Preserve Studio composer navigation blocking: dirty Agent Configuration state, unconfirmed Agent Configuration operations and unknown workspace operations continue to participate in the existing blocker/lock semantics.
- Preserve specialised early-return boundaries: `AgentConfigurationScreen` and `ToolAuthoringScreen` remain outside the generic `<main>` page/detail router and retain their current props/data handoff.
- Preserve `StudioComposerContext`, `DirtyNavigationGuard`, `StudioState`, `ToolAuthoringScreen`, `AgentConfigurationScreen`, `AdminExplorer` and `src/studio/server-actions.ts` as canonical existing owners. Do not create a new router, plugin framework, command bus, state store or DI framework.
- Preserve exact current strings/routes/role gates and current source quirks during extraction. Do not opportunistically redesign Shop search/Preview/Test links, dirty clearing, validation messages or confirmation behaviour.
- These tests are frozen byte-for-byte throughout COMMERCE-001..005: `tests/studio-workspace.test.tsx` (`400ce6b68cb5a9fdeecf9233bc2b3f58a42742c974da2c5b6ffd2b5a16ae44a7`, 13 tests), `tests/agent-configuration-screen-state.test.tsx` (`72c71a09eaf5bdc2d79c686cf5ec43d5abfd49cfe421cadedbbe665140582b0a`, 3 tests), `tests/external-tools-ui.test.tsx` (`97ffbc70e29d4ff60a48e5aabd0ff3faec6dea7984ed0f239fcb4a8fc868f4d3`, 90 tests).
- `tests/legacy-capability-surface.test.ts` and `tests/arch024-preview-cleanup.test.ts` may be changed only by COMMERCE-001 and only to make their source loader follow the bounded StudioWorkspace module set without deleting/weakening existing assertions. COMMERCE-002..005 must not modify the accepted COMMERCE-001 versions.
- No ARCH-025 Commerce task may modify the adjacent canonical owner files listed in the parent regression baseline except for import-only changes explicitly authorised by that task.
- Keep tests honest: no skipped/only/todo tests, weakened expectations or new behavioural expectations merely to accommodate extraction.

### R1 — Release Composer ownership

Move the entire current `ReleaseComposer` workflow into `components/studio-workspace/release-composer.tsx`. Release-specific state remains local to that component: open/closed state, exact members/positions, capability options, instructions, raw schema text, publication reason, validation state/pending/generation/hash refs. Do not move it into the global workspace controller.

### R2 — initial seed/default semantics

Preserve seed precedence exactly: `composer.release` before the currently ACTIVE release before the existing default response contract/instructions/reason. Preserve `open = Boolean(seed)`. Continue loading `listReleaseCapabilities()` once on mount and ignore non-OK results as today.

### R3 — candidate parsing/freshness

Preserve `CommerceResponseContractSchema.safeParse(...)`, raw invalid JSON retention, `JSON.stringify({ members, responseContract })` canonical input hash, generation token, duplicate-validation guard and current-input-hash fence. Member/instructions/schema changes mark dirty and stale validation; publication-reason changes mark dirty but do **not** stale validation. An old asynchronous validation result must never validate newer content.

### R4 — role/create/cancel semantics

Preserve the current asymmetric role behaviour exactly. The top-level **Create release** opener is shown only to `SUPER_ADMIN`, while `ADMIN` receives the explanatory copy. However, when the composer is already open from `composer.release` seed state (for example via Edit as new release), the inner **Create immutable release** button is currently gated only by `pending || locked || !validated` and is not independently hidden/disabled by role; server authorization remains authoritative. Do not add a new client role gate during extraction. Preserve the exact create payload, success navigation to `/releases/<id>?tab=response-contract`, and `DirtyNavigationGuard` Cancel behaviour. Do not restore any obsolete Preview/Test handoff.


## Work Items

- [x] Move Release Composer into the dedicated module.
- [x] Keep all Release-specific state/validation local to that module.
- [x] Add focused Release Composer tests for seed/default/freshness/single-flight/create/cancel behaviour.
- [x] Keep the accepted COMMERCE-001 controller and source-inspection tests unchanged.


## Interfaces / Contracts

Consumes the accepted COMMERCE-001 common workspace props/command contract. Release candidate state remains module-local.

## Dependencies

- `ARCH-025-COMMERCE-001`

## Enables

- `ARCH-025-COMMERCE-003`

## Acceptance Criteria

- [x] Releases page renders the same records/composer UI through the extracted module.
- [x] Validation freshness/single-flight/hash semantics are unchanged.
- [x] Publication reason still does not stale validation.
- [x] No Preview handoff or new server action is introduced.
- [x] SUPER_ADMIN-only opener / seeded-composer ADMIN submission asymmetry is unchanged; no new client create-role gate is introduced.
- [x] Frozen 13/3/90-test assets and accepted COMMERCE-001 source-inspection tests are unchanged; frozen hashes match. The StudioWorkspace suite retains its six documented baseline failures.


## Validation

- [x] Frozen-hash Node check prints all three expected SHA-256 hashes.
- [x] `npx vitest run tests/release-composer.test.tsx` passes: 7 tests.
- [x] Required combined focused command: 17 passed; the six failures are the documented `tests/studio-workspace.test.tsx` failures in `ARCH025-COMMERCE-TEST-001`.
- [x] `git diff -- tests/legacy-capability-surface.test.ts tests/arch024-preview-cleanup.test.ts` is empty.

- [x] `npm test` executed: 34 failed, 1,346 passed, 9 skipped; six collection failures and stable failures match `ARCH025-COMMERCE-TEST-001`. Three out-of-baseline assertions passed when rerun individually; two documented failures disappeared. No task-owned Release Composer test failed.
- [x] `npm run typecheck` passes.
- [x] Targeted ESLint on all three changed Commerce source/test files passes.
- [x] `npm run build` succeeds (existing Nunjucks dynamic-dependency warnings only).
- [x] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Commerce task.

## Implementation Notes

None

## Completion Report

### Status

Ready for Review

### Files Changed

`components/studio-workspace.tsx`; `components/studio-workspace/release-composer.tsx`; `tests/release-composer.test.tsx`.

### Work Completed

Extracted the complete Release Composer workflow and its candidate/validation state into the dedicated module. Added seven focused tests covering seed/default precedence, capability load, ADMIN seeded submission, create payload/navigation, pending/locked guards, validation freshness and duplicate/late validation, and guarded cancellation. The exact operation, navigation and authorization semantics remain unchanged; the accepted COMMERCE-001 controller and source-inspection tests were not modified.

### Validation Results

Passed: focused Release Composer tests (7/7); typecheck; targeted ESLint; production build; frozen SHA-256 checks; source-inspection test diff check; `git diff --check`.

Environment verified in the implementation worktree using `scripts/bootstrap-node.sh`: Node `v24.19.0`, npm `11.17.0`, Vitest `5.0.1`; `npm ls --depth=0` resolved successfully. `package-lock.json` SHA-256 is `d8ebcf87bcd1ce0c9d2b62b88784abf359697e9149d97eadd04f97af04469d35`; recursive submodule `database` is pinned at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.

Required combined focused run: 17 passed / 6 failed; all six failures are the documented StudioWorkspace failures in `ARCH025-COMMERCE-TEST-001`.

Full `npm test`: 1,346 passed / 34 failed / 9 skipped. The six documented collection failures and stable documented assertion failures remain. `discount-reader`, `feature-configuration-screen`, and the readiness abort-timeout assertion failed only in the full run and passed in isolated reruns; two failures listed in the baseline did not recur. No focused Release Composer test failed. Treat the full-suite-only variance as unresolved suite-level evidence, not as a pass.

### Deviations

No product-behaviour changes. Full-suite result remains non-green and includes three out-of-baseline assertions that passed in isolated reruns; architect review should account for this suite-level variance.

### Assumptions

Used the supplied prepared worktrees and the active Attempt 1 claim. The implementation task branch began at current `origin/main`; no implementation remote task ref existed before this first push. The parent task claim/remote branch was already present. `package-lock` and database submodule state matched the supplied environment evidence.

### Unresolved Issues

Full repository suite remains non-green as detailed above; no Release Composer-specific failure was observed.

### Architectural Concerns

No cross-repository or architecture contract concerns.

### Git / VCS

Task branch: `task/ARCH-025-COMMERCE-002`

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-COMMERCE-002`
  parent branch: `task/ARCH-025-COMMERCE-002`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-COMMERCE-002`
  implementation branch: `task/ARCH-025-COMMERCE-002`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization: launcher-prepared; both task worktrees were reused. Implementation `origin/main` was already included; implementation remote task branch was absent before initial publication. Parent remote task claim was already present.

Implementation repository:
  repository: `moda-interact-commerce`
  commit: `3352a9a761d84bb00e37650f02487efed619e118`
  remote branch: `origin/task/ARCH-025-COMMERCE-002`
  pushed: yes; remote ref verified at the implementation commit

Parent workspace:
  task file: `docs/decisions/commerce/ARCH-025/COMMERCE-002-extract-release-composer.md`
  review-submission commit: `d98207c9feee116c7738f0404887db584f355db6`
  remote branch: `origin/task/ARCH-025-COMMERCE-002`
  pushed: yes; remote ref verified at the review-submission commit
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status

Accepted — Attempt 1

### Review Notes

The Release Composer extraction is architecture-conformant and remains a move-only structural refactor. Direct comparison against the accepted COMMERCE-001 StudioWorkspace baseline shows the complete Release Composer body — from its first composer-state read through its rendered JSX — is byte-for-byte identical after extraction. `components/studio-workspace.tsx` only drops the Release-specific imports/server-action aliases/local component body and imports the dedicated `ReleaseComposer`; no controller, Release Detail, Shop, generic routing, server-action or contract behaviour is redesigned.

Seed precedence, `open = Boolean(seed)`, one-time capability loading, raw invalid-schema retention, canonical validation hash, generation/current-input fencing, duplicate validation suppression, publication-reason freshness asymmetry, SUPER_ADMIN opener/seeded ADMIN submission asymmetry, exact create payload/navigation, dirty handling and guarded Cancel semantics are preserved. The new focused tests exercise the important extraction boundary without changing the frozen regression assets.

`ARCH025-COMMERCE-TEST-001` correctly governs the non-green broad-suite result. The required combined run retains the same six documented frozen StudioWorkspace failures. Full `npm test` improves relative to the accepted COMMERCE-001 submitted reference: two documented failures no longer occur and must not be recreated. Three assertions outside the durable baseline failed only in the broad run, were investigated, and passed isolated reruns; they are in untouched Discount Reader, Feature Configuration and readiness areas rather than the Release Composer extraction. They are not added to the baseline. No task-owned Release Composer failure was observed.

The Completion Report records launcher-prepared dedicated parent/Commerce worktrees, matching task branches, no shared/other-task worktree reuse, start-of-attempt synchronization, the exact `cfeeb12456b4e05067a96857a8c47837d7e33bbd` recursive Database submodule state, clean pushed task branches and the submitted implementation commit `3352a9a761d84bb00e37650f02487efed619e118`. The final handoff identifies parent report head `f2e132a`; the report's self-contained Git/VCS section necessarily records its earlier review-submission commit `d98207c9feee116c7738f0404887db584f355db6`.

### Reviewed Files

- `components/studio-workspace.tsx`
- `components/studio-workspace/release-composer.tsx`
- `tests/release-composer.test.tsx`
- frozen `tests/studio-workspace.test.tsx`
- frozen `tests/agent-configuration-screen-state.test.tsx`
- frozen `tests/external-tools-ui.test.tsx`
- accepted COMMERCE-001 `tests/legacy-capability-surface.test.ts` and `tests/arch024-preview-cleanup.test.ts`
- `docs/development-baseline.md` (`ARCH025-COMMERCE-TEST-001`)
- Completion Report and VCS/environment evidence

### Validation Reviewed

- Frozen SHA-256 checks: all three expected hashes match.
- Focused `tests/release-composer.test.tsx`: 7/7 passed.
- Required combined focused run: 17 passed / 6 failed; all six failures are the documented frozen StudioWorkspace failures in `ARCH025-COMMERCE-TEST-001`.
- Accepted COMMERCE-001 source-scanner files: byte-identical.
- Full `npm test`: 1,346 passed / 34 failed / 9 skipped; stable failures/collection failures remain governed by `ARCH025-COMMERCE-TEST-001`, two documented failures disappear, and three out-of-baseline broad-run assertions pass their isolated reruns.
- `npm run typecheck`: passed.
- Targeted ESLint on the three changed source/test files: passed.
- `npm run build`: passed with the existing Nunjucks dynamic-dependency warnings only.
- `git diff --check`: passed.
- Review archive has no installed `node_modules`, so dependency-backed commands were inspected from durable task evidence rather than replayed in the review container.

### Architecture Conformance

Accepted. COMMERCE-002 preserves the public StudioWorkspace boundary and all Release composition behaviour while moving only the Release Composer's local lifecycle into its dedicated owner. No cross-repository contract, persistence, authorization or product-behaviour change is introduced. Under `completion_mode: automatic`, the task becomes Complete.

### Follow-up

`ARCH-025-COMMERCE-003` now has all dependencies Complete and is promoted from Pending to Ready. It is not claimed or started by this reconciliation. Continue to use `ARCH025-COMMERCE-TEST-001` only for its exact documented stable failures; disappearing failures remain improvements and any new/changed failure must still be investigated.
