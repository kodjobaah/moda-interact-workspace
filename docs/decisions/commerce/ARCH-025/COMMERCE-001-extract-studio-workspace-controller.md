---
id: ARCH-025-COMMERCE-001
architecture_id: ARCH-025
title: Extract StudioWorkspace controller and extraction-safe source assertions
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 20
executor: copilot
claimed_at: 2026-10-02T22:26:57Z
attempt: 2
depends_on:
  - ARCH-024-COMMERCE-003
enables:
  - ARCH-025-COMMERCE-002
created: 2026-10-02
updated: 2026-10-02
---

# Extract StudioWorkspace controller and extraction-safe source assertions

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the global Studio workspace orchestration into a complete typed controller while retaining the public shell and making existing source-inspection assertions follow the bounded StudioWorkspace module set.

## Context

The current shell mixes route loading, stale-load protection, global dirty/navigation state and command admission/reconciliation with substantial page JSX. Every later Commerce task depends on one stable orchestration interface, so this task establishes that interface before presentation/workflow extraction starts.

## Scope

Authorised implementation surface:

```text
components/studio-workspace.tsx
components/studio-workspace/studio-workspace.types.ts
components/studio-workspace/use-studio-workspace-controller.ts
tests/studio-workspace-controller.test.tsx
tests/legacy-capability-surface.test.ts
tests/arch024-preview-cleanup.test.ts
```

## Out of Scope

Release Composer/Detail extraction, Shop view extraction, generic page-router extraction, Tool/Agent Configuration implementation changes, server-action changes or persistence changes.

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

### R1 — complete workspace controller contract

Create an internal typed/controller boundary that owns route identity, result/detail/loaded identity, hydration suppression, load token, global message/pending/dirty state, Agent Configuration dirty/unconfirmed state, unknown-operation state, completion token, content revision, navigation-blocker registration, `load`, `runCommand` and `reconcile`. The accepted controller must expose every global value/action consumed by COMMERCE-002..005; later tasks are consume-only. If a later task discovers a missing controller interface, it must stop and return to `moda_architect` rather than silently extending the controller.

### R2 — route/load semantics

Preserve the exact current route/load behaviour. `routeIdentity` includes `authoringSessionId`; the load effect dependencies remain `page`, `detailId`, `revisionId`. Initial hydrated identity suppresses one duplicate load. `loadToken` prevents stale list/detail results from overwriting newer route data. `agent-configuration` sets the bounded local result/detail/loaded identity without a Studio server action. Tools/Explore/Releases/Shops retain the current list/detail call selection/order.

### R3 — command/unknown reconciliation

Preserve `pendingRef` admission, completion token, unexpected thrown-failure classification, unknown-operation storage and reconciliation of the **original** operation ID/run callback/admitted revision. Preserve the exact operation-ID generator and expose it as a repository-internal helper usable by later Release Detail extraction.

### R4 — extraction-safe source inspection

Change only source-loading mechanics in `legacy-capability-surface.test.ts` and `arch024-preview-cleanup.test.ts` so the existing assertions scan `components/studio-workspace.tsx` plus direct `.ts`/`.tsx` modules under `components/studio-workspace/` in deterministic order, while retaining `studio-composer-context.tsx` in the ARCH-024 human-handoff scan. Do not remove or weaken legacy-token/obsolete-Preview assertions.

### R5 — focused controller tests

Add focused tests proving hydration suppression, stale-load rejection, no reload on authoring-session-only change, single-flight/unknown-operation admission, reconciliation with the original operation ID and content-revision dirty fencing.

### R6 — preserve current cross-route/global-state asymmetries

Do not introduce route-change resets that do not exist today. In particular, route changes must not opportunistically clear `message`, global `dirty`, Agent Configuration dirty/unconfirmed state or an unresolved `unknown` operation. Preserve the current global navigation-blocker `onDiscard` behaviour, which clears only the workspace `dirty` flag; Agent Configuration owns its own dirty/unconfirmed convergence. Existing 13/3/90-test assets remain unchanged.


## Work Items

- [x] Introduce `studio-workspace.types.ts` and `use-studio-workspace-controller.ts` with the complete downstream contract.
- [x] Rewire the existing monolithic shell/pages to consume the controller without moving Release/page JSX yet.
- [x] Add focused controller tests.
- [x] Make the two source-inspection harnesses extraction-safe without changing their assertions.
- [x] Prove all frozen integration/state assets remain byte-identical.


## Interfaces / Contracts

Internal Commerce UI controller/type contract only. `components/studio-workspace.tsx` remains the public compatibility boundary; no cross-repository contract is introduced.

## Dependencies

- `ARCH-024-COMMERCE-003` — Complete and integrated; establishes the final Studio model-selection shape before this high-churn component is structurally extracted.

## Enables

- `ARCH-025-COMMERCE-002`

## Acceptance Criteria

- [x] Existing production callers continue importing `StudioWorkspace` / `StudioPage` from `components/studio-workspace.tsx`.
- [x] Route/hydration/load and write/unknown reconciliation behaviour is unchanged.
- [x] Controller contract is sufficient for COMMERCE-002..005 without later controller redesign.
- [x] Source-inspection assertions cover the bounded extracted module set and retain every current assertion.
- [ ] Frozen 13/3/90-test assets are unchanged and pass. The files are byte-identical, but the required Studio browser suite has six failures; see Validation Results and Unresolved Issues.


## Validation

- [x] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/studio-workspace.test.tsx':'400ce6b68cb5a9fdeecf9233bc2b3f58a42742c974da2c5b6ffd2b5a16ae44a7','tests/agent-configuration-screen-state.test.tsx':'72c71a09eaf5bdc2d79c686cf5ec43d5abfd49cfe421cadedbbe665140582b0a','tests/external-tools-ui.test.tsx':'97ffbc70e29d4ff60a48e5aabd0ff3faec6dea7984ed0f239fcb4a8fc868f4d3'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected frozen hashes.
- [ ] `npx vitest run tests/studio-workspace-controller.test.tsx tests/studio-workspace.test.tsx tests/agent-configuration-screen-state.test.tsx tests/external-tools-ui.test.tsx tests/legacy-capability-surface.test.ts tests/arch024-preview-cleanup.test.ts` passes. It reports 6 failed and 116 passed; failures are all in unchanged `tests/studio-workspace.test.tsx`.

- [ ] `npm test` passes without task-introduced regression. Full run: 30 failed, 128 passed, 5 skipped; 65 failed, 1,308 passed, 9 skipped. Detailed failures include the unchanged Studio browser and Tool Authoring screen suites.
- [x] `npm run typecheck` passes after Prisma Client generation.
- [x] targeted `npm run lint -- <changed Commerce source/test files>` (or repository-equivalent targeted ESLint invocation using the declared lint script) exits successfully; two hook-dependency warnings are reported in untouched `src/studio/code-response/code-response-panel.tsx`.
- [x] `npm run build` succeeds; Next reports the existing Nunjucks dynamic-require warning.
- [x] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Commerce task.

## Implementation Notes

None

## Completion Report

### Status

Ready for Architect Review; frozen-suite acceptance remains unresolved.

### Files Changed

- `moda-interact-commerce/components/studio-workspace.tsx`
- `moda-interact-commerce/components/studio-workspace/studio-workspace.types.ts`
- `moda-interact-commerce/components/studio-workspace/use-studio-workspace-controller.ts`
- `moda-interact-commerce/tests/studio-workspace-controller.test.tsx`
- `moda-interact-commerce/tests/legacy-capability-surface.test.ts`
- `moda-interact-commerce/tests/arch024-preview-cleanup.test.ts`

### Work Completed

- Claimed Commerce Attempt 1 as `copilot` (claim commit `5e9ca7b83b553eb925c8c82218a6cdc1626a7a37`); dependency `ARCH-024-COMMERCE-003` passed.
- Implementation ran in `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-COMMERCE-001`, on `task/ARCH-025-COMMERCE-001`; parent report ran in `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-COMMERCE-001`.
- Extracted route/load orchestration, global command admission, unknown-operation reconciliation, dirty revision fencing and navigation-blocker state into the typed hook. Kept public shell/type exports, specialized early-return boundaries, server actions and page JSX in their existing owners.
- Added five focused controller cases and updated only the source-loading mechanics in the two authorized source-inspection tests; existing assertions were retained.
- Verified the three frozen files against their required SHA-256 values. No frozen test asset was edited.
- Installed the locked npm dependencies and generated Prisma Client from the canonical schema before typecheck/build validation. Commerce is at Node `v24.19.0`; submodule `database` is at `cfeeb12456b4e05067a96857a8c47837d7e33bbd` (`heads/main`).

### Validation Results

- `npx vitest run tests/studio-workspace-controller.test.tsx tests/legacy-capability-surface.test.ts tests/arch024-preview-cleanup.test.ts`: passed, 3 files / 8 tests.
- Required six-file focused Vitest command: 6 failed, 116 passed, 122 total; only the unchanged `tests/studio-workspace.test.tsx` file failed.
- `npm test`: 30 failed, 128 passed, 5 skipped across 163 files; 65 failed, 1,308 passed, 9 skipped. Existing broad-suite failures are outside the controller/scanner tests; detailed output included `tests/tool-authoring-screen.test.tsx` timing out.
- `npm run typecheck`: passed.
- Targeted ESLint command: exit 0, 0 errors; two warnings in untouched `src/studio/code-response/code-response-panel.tsx`.
- `npm run build`: passed; includes successful manual/runtime packaging smoke checks and production build. Next emitted a Nunjucks dynamic-require warning.
- Frozen hashes: all three expected SHA-256 values matched.
- `git diff --check`: passed.

### Deviations

The frozen Studio browser suite and full repository suite do not pass. The frozen test files remain byte-identical, and no canonical Tool Authoring/UI owner or frozen test was changed because doing so would exceed this task's move-only authorized scope. Architect review should determine whether these are baseline test/production mismatches or require a separate task before accepting the frozen-suite criterion.

### Assumptions

The downstream controller contract is adequate for COMMERCE-002..005 based on the values/actions consumed by the retained shell and the focused behavior tests; later tasks remain consume-only as specified.

### Unresolved Issues

The frozen `tests/studio-workspace.test.tsx` failures include new-tool tests querying authoring fields without invoking the existing Tool Library create action, and detail-edit tests querying `Save draft` while the existing editor is on the `Request` tab. The original committed shell invokes the unchanged `ToolAuthoringScreen` with the same props; this extraction did not alter that screen. The full test command also reports 65 failures overall, including a timeout in `tests/tool-authoring-screen.test.tsx`. These failures need architect classification; the explicit frozen-suite pass criterion is not met.

### Architectural Concerns

No new router, command bus, state store or dependency-injection layer was introduced. No server-action signatures, persistence behavior, canonical owner files or frozen test assets were changed. Do not start `ARCH-025-COMMERCE-002` until architect review resolves the failed validation gate.

## Architect Review

### Review Status

Changes Requested — Attempt 1

### Review Notes

The structural implementation is architecture-conformant on source inspection and no controller source correction is requested at this stage. The extracted hook owns the required route/result/detail/loaded identities, hydration and stale-load fencing, message/pending/dirty and Agent Configuration navigation state, write single-flight, operation identity, unknown reconciliation, completion/content revisions, navigation-blocker registration, `load`, `runCommand` and `reconcile`. The public `StudioWorkspace` / `StudioPage` boundary and specialised Tool/Agent Configuration early returns remain intact. The two authorised source scanners now read the public shell plus direct `components/studio-workspace/` modules in deterministic order without deleting or weakening their existing assertions.

The three frozen assets and all parent-listed adjacent canonical owners were independently hash-checked against the ARCH-025 regression baseline and remain byte-identical. Direct comparison with the reviewed pre-extraction StudioWorkspace baseline found the orchestration logic moved into the controller without an identified behavioural redesign.

Acceptance is withheld for validation classification and deterministic execution evidence.

**A1-R1 — classify the frozen-suite and package-wide failures against the exact pre-task Commerce tree.**

The task requires the frozen Studio command and full `npm test` validation to introduce no task regression, but Attempt 1 records six failures in unchanged `tests/studio-workspace.test.tsx` and 65 failures in the full suite without an accepted ARCH-025 Commerce baseline ID or a same-environment pre-task/submitted comparison. The six frozen failure names are known from earlier Commerce evidence to predate this extraction, but that evidence is not yet an accepted ARCH-025 development-baseline entry and does not classify the current 65-failure full-suite run.

Attempt 2 MUST run, under the same Node/npm/dependency/database-submodule/environment state, both (a) the exact required six-file frozen/focused command and (b) the exact full `npm test` command on the launcher-recorded synchronized pre-task Commerce commit and on the submitted COMMERCE-001 implementation head. Record the exact failing test and collection identifiers for both trees.

If the submitted frozen failures are identical to or better than the pre-task set and the full suite has no new or worsened COMMERCE-001-owned failure, no implementation-source change is required. Record that parity explicitly so `moda_architect` can establish/reuse a durable ARCH-025 Commerce baseline rather than forcing later extraction tasks to rediscover it. If the submitted tree introduces a new or worsened failure, investigate and correct only the task-owned regression before resubmission. Do not edit frozen assets, canonical adjacent owners or production behaviour merely to manufacture a green suite.

The Attempt 2 Completion Report must also write the Vitest summaries unambiguously as file counts and test counts; the Attempt 1 `npm test` summary currently mixes both aggregate forms in one bullet.

**A1-R2 — durably record the deterministic prepared-execution packet.**

The report names the dedicated parent/implementation worktree paths and Attempt 1 claim commit, but it does not contain the complete launcher-resolved start-of-attempt synchronization evidence required by `docs/agent-worktree-isolation-policy.md`. Attempt 2 MUST record the actual prepared packet, including:

```text
canonical workspace_root
dedicated parent task worktree + task/ARCH-025-COMMERCE-001 branch
dedicated Commerce implementation worktree + task/ARCH-025-COMMERCE-001 branch
shared/default checkout not used for task edits
previous/other task worktree not reused

parent task-branch synchronization and origin/main incorporation
implementation task-branch synchronization and origin/main incorporation
dependency gate for ARCH-024-COMMERCE-003
git submodule sync --recursive
git submodule update --init --recursive
exact database submodule/gitlink identity

Attempt 2 claim metadata + durable claim commit
submitted implementation head + remote task-branch head
final parent report head + remote task-branch head
final clean status and local-head == remote-task-head for both worktrees
```

A1-R2 is evidence-only. Do not create implementation churn solely to produce a new source commit.

### Reviewed Files

- `components/studio-workspace.tsx`
- `components/studio-workspace/studio-workspace.types.ts`
- `components/studio-workspace/use-studio-workspace-controller.ts`
- `tests/studio-workspace-controller.test.tsx`
- `tests/legacy-capability-surface.test.ts`
- `tests/arch024-preview-cleanup.test.ts`
- frozen `tests/studio-workspace.test.tsx`
- frozen `tests/agent-configuration-screen-state.test.tsx`
- frozen `tests/external-tools-ui.test.tsx`
- parent-listed frozen adjacent Studio owner files

### Validation Reviewed

- Controller/scanner focused run reported 8/8 passed.
- Frozen SHA-256 checks independently matched all three required values.
- Adjacent-owner SHA-256 checks independently matched the parent ARCH-025 regression baseline.
- Required six-file command reported 116 passed / 6 failed; failures are confined to the byte-identical frozen `tests/studio-workspace.test.tsx`, but pre-task parity has not yet been durably established for this task.
- Full suite reported 1,308 passed / 65 failed / 9 skipped; current failing identities are not sufficiently classified against the exact pre-task Commerce tree.
- Typecheck, targeted lint, production build and `git diff --check` are reported passing.

### Architecture Conformance

Implementation shape conforms to the move-only controller extraction and source-scanner ownership boundaries. Acceptance remains gated on A1-R1/A1-R2 evidence, not on an identified controller design defect.

### Follow-up

Return the same task through `/moda-task ARCH-025-COMMERCE-001`. Attempt 2 should be evidence-first. Do not start `ARCH-025-COMMERCE-002` until COMMERCE-001 is architect-accepted Complete.
