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
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-024-COMMERCE-003
enables:
  - ARCH-025-COMMERCE-002
created: 2026-10-02
updated: 2026-10-03
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
- [x] Frozen 13/3/90-test assets are unchanged. The six Studio browser failures are identical on the synchronized pre-task tree; the other frozen suites pass on both trees in the required focused command.


## Validation

- [x] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/studio-workspace.test.tsx':'400ce6b68cb5a9fdeecf9233bc2b3f58a42742c974da2c5b6ffd2b5a16ae44a7','tests/agent-configuration-screen-state.test.tsx':'72c71a09eaf5bdc2d79c686cf5ec43d5abfd49cfe421cadedbbe665140582b0a','tests/external-tools-ui.test.tsx':'97ffbc70e29d4ff60a48e5aabd0ff3faec6dea7984ed0f239fcb4a8fc868f4d3'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected frozen hashes.
- [x] `npx vitest run tests/studio-workspace-controller.test.tsx tests/studio-workspace.test.tsx tests/agent-configuration-screen-state.test.tsx tests/external-tools-ui.test.tsx tests/legacy-capability-surface.test.ts tests/arch024-preview-cleanup.test.ts` has no task-introduced failure: baseline reports 6 failed / 111 passed across the five files present at the pre-task commit; submitted reports 6 failed / 116 passed across six files. The same six failures occur in unchanged `tests/studio-workspace.test.tsx`; the submitted controller suite adds five passing tests.

- [x] `npm test` comparison shows no new or worsened COMMERCE-001-owned failure. Baseline: 29 failed files / 65 failed tests, 128 passed files / 1,303 passed tests, 5 skipped files / 9 skipped tests (162 files total). Submitted: 23 failed files / 38 failed tests, 135 passed files / 1,335 passed tests, 5 skipped files / 9 skipped tests (163 files total). Exact identity comparison and run-variance analysis are recorded below.
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

Ready for Architect Review; A1-R1 and A1-R2 evidence supplied in Attempt 2.

### Files Changed

- `moda-interact-commerce/components/studio-workspace.tsx`
- `moda-interact-commerce/components/studio-workspace/studio-workspace.types.ts`
- `moda-interact-commerce/components/studio-workspace/use-studio-workspace-controller.ts`
- `moda-interact-commerce/tests/studio-workspace-controller.test.tsx`
- `moda-interact-commerce/tests/legacy-capability-surface.test.ts`
- `moda-interact-commerce/tests/arch024-preview-cleanup.test.ts`

### Work Completed

- Attempt 1 was claimed by `copilot` (claim commit `5e9ca7b83b553eb925c8c82218a6cdc1626a7a37`); Architect requested evidence-only rework. Attempt 2 was claimed by `copilot` at `2026-10-02T22:26:57Z` (durable parent claim commit `bdb36a5d7f9670b25cdff05ae870f8b91e2fabe2`); dependency `ARCH-024-COMMERCE-003` passed.
- Implementation ran in `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-COMMERCE-001`, on `task/ARCH-025-COMMERCE-001`; parent report ran in `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-COMMERCE-001`.
- Attempt 2 launcher packet: canonical `workspace_root` `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; dedicated parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-COMMERCE-001` and Commerce implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-COMMERCE-001`, both on `task/ARCH-025-COMMERCE-001`. Shared/default checkouts were not used for task edits; no other task worktree was reused.
- Start-of-attempt synchronization: parent task branch fast-forward `not-needed`, `origin/main` incorporated `yes`, parent pre-claim head `9e2c24edab831e63bbd2d065b1e83a6d5e8afb51`; implementation task branch fast-forward `not-needed`, `origin/main` incorporation `already-current`, implementation pre-edit head `b1f3cc6e75d9d8f78d1087cb6dcc1375801f0809`.
- Recursive implementation submodules: launcher `git submodule sync --recursive` passed and `git submodule update --init --recursive` passed. `database` was initialized at exact gitlink `cfeeb12456b4e05067a96857a8c47837d7e33bbd` (`heads/main`).
- The submitted implementation head and `origin/task/ARCH-025-COMMERCE-001` are both `b1f3cc6e75d9d8f78d1087cb6dcc1375801f0809`; the implementation worktree is clean. Parent report claim head was `bdb36a5d7f9670b25cdff05ae870f8b91e2fabe2`; final parent local/remote equality and clean status are verified after this report update is published.
- Extracted route/load orchestration, global command admission, unknown-operation reconciliation, dirty revision fencing and navigation-blocker state into the typed hook. Kept public shell/type exports, specialized early-return boundaries, server actions and page JSX in their existing owners.
- Added five focused controller cases and updated only the source-loading mechanics in the two authorized source-inspection tests; existing assertions were retained.
- Verified the three frozen files against their required SHA-256 values. No frozen test asset was edited.
- Installed the locked npm dependencies and generated Prisma Client from the canonical schema before typecheck/build validation. Commerce is at Node `v24.19.0`; submodule `database` is at `cfeeb12456b4e05067a96857a8c47837d7e33bbd` (`heads/main`).

### Validation Results

- `npx vitest run tests/studio-workspace-controller.test.tsx tests/legacy-capability-surface.test.ts tests/arch024-preview-cleanup.test.ts`: passed, 3 files / 8 tests.
- Comparison environment: Node `v24.19.0`, npm `11.17.0`, Vitest `5.0.1`, same installed `node_modules`, identical `package-lock.json` SHA-256 `d8ebcf87bcd1ce0c9d2b62b88784abf359697e9149d97eadd04f97af04469d35`, unchanged package manifests, and the same `database` submodule commit. Baseline source was materialized from launcher-recorded synchronized pre-task commit `f9fa054b74e367fd8968fd7c26336657e945a174`; submitted source was `b1f3cc6e75d9d8f78d1087cb6dcc1375801f0809`. Runs were sequential; the full-suite baseline was rerun after an earlier overlapping/invalid attempt.
- Required focused Vitest command: baseline 1 failed / 4 passed files and 6 failed / 111 passed tests (the new controller test file is absent at the pre-task commit); submitted 1 failed / 5 passed files and 6 failed / 116 passed tests. The identical six failures on both trees are: `exposes the failure class when a named Studio action rejects unexpectedly`; `authors a reusable tool without publishing and navigates to its returned ID`; `retains incremental invalid JSON and saves only the complete canonical tool definition`; `resets editor state when a mounted detail changes to another record`; `keeps newer edits dirty when an earlier save completes`; and `retains editor input after stale CAS`. All are in unchanged `tests/studio-workspace.test.tsx`. Baseline and submitted `tests/agent-configuration-screen-state.test.tsx`, `tests/external-tools-ui.test.tsx`, both source scanners, and the submitted controller tests pass in this focused command.
- `npm test` baseline: 29 failed files / 65 failed tests, 128 passed files / 1,303 passed tests, 5 skipped files / 9 skipped tests (162 files total). Submitted: 23 failed files / 38 failed tests, 135 passed files / 1,335 passed tests, 5 skipped files / 9 skipped tests (163 files total). Both runs have the same six collection failures: `tests/agent-configuration-model-postgres.test.ts`, `tests/agent-configuration-prompts-postgres.test.ts`, `tests/c20-integration-fixture.test.ts`, `tests/local-external-mcp-diagnostic.test.ts`, `tests/preview-openrouter-postgres.test.ts`, and `tests/studio-integration-c20.test.ts`.
- Exact full-suite test-level intersection (33 identities):
  - `tests/admin-explorer.test.tsx`: `preserves a valid manual query that is not representable and returns it unchanged`; `builds and validates a representable selection before merging query fields into an existing draft`; `keeps exact raw text for an unchanged literal mapping and drops stale buffers`; `round-trips a newly visual-authored string literal through the New Tool Request editor`; `validates Request query while preserving malformed unrelated editor buffers`; `shows validation progress while the Shopify Admin validation request is in flight`; `validates a restored visual selection even when the selected root field is outside the loaded schema page`; `keeps Validate available when the visual candidate cannot yet be built and reports the blocking reason`; `offers a return action beside validation without applying temporary Explorer state`; `cancel returns to the validated origin without merging temporary Explorer state`.
  - `tests/admin-graphql-compiler.test.ts`: `rejects nullable input schemas for non-null variables`.
  - `tests/agent-configuration-retained-read.test.ts`: `tracks model and prompt CAS versions on one retained row across clear operations`.
  - `tests/agent-contract-validation.test.ts`: `rejects unknown scalar paths and non-list items paths`.
  - `tests/auth-entrypoints.test.ts`: `keeps NextAuth and health public while the MCP route remains private`.
  - `tests/backend-postgres-rehearsal.test.ts`: `publishes once, replays durably, rejects stale CAS, races across connections, and rolls back injected failure`.
  - `tests/discount-evaluator.test.ts`: `retains preview purpose, environment, and trace correlation in eligibility telemetry`.
  - `tests/discovery-limits.test.ts`: `allows 60 sequential requests and rejects the 61st in the rolling window`.
  - `tests/external-tools-ui.test.tsx`: `does not create a live-test receipt from Automatic generation and keeps publication gated`; `traverses new external tool authoring through U06, U14, return context and publish`.
  - `tests/health.test.ts`: `readiness checks required dependencies and has no release-publication dependency`; `bounds hanging dependencies under two seconds and aborts Redis`.
  - `tests/merchant-knowledge-embedding.test.ts`: `validates the exact OpenAI provenance environment contract`.
  - `tests/policy-operation-authoring-server-actions.test.ts`: `returns UNAVAILABLE for invalid or unregistered operation identities without fallback`.
  - `tests/policy-operation-result-template.test.ts`: `reports whether each currently registered operation result is template-compatible`.
  - `tests/preview-page.test.tsx`: `projects only browser-safe selected-Shop configuration and Feature fields`; `never forwards an invalid URL Shop ID as the selected Shop`.
  - `tests/readiness-docker.test.ts`: `kills ignored-stdio descendants after leader exit on timeout`.
  - `tests/studio-workspace.test.tsx`: all six focused failure identities listed above.
- Baseline-only full-run test identities (32): `tests/auth-entrypoints.test.ts > adds no duplicate NextAuth account tables and never changes merchant permission models`; `tests/code-request-processor.test.ts > returns a deterministic canonical descriptor`; `rejects unsafe output through the Commerce descriptor schema`; `does not expose network or host capabilities`; `rejects unsafe request output values through the processor`; `rejects unsafe args, oversized input, missing entrypoints, and cancellation`; `tests/code-response-processor.test.ts > transforms JSON through the accepted kernel`; `transforms TEXT without attempting JSON parsing`; `runs v2 with Moda helpers and keeps unsupported versions unavailable`; `rejects malformed responses and non-object output roots`; `maps syntax, deadline, cancellation, and output-limit failures`; `keeps simultaneous inputs isolated`; `leaves result-schema enforcement at the Shared validation boundary`; `tests/code-runtime-proof.test.ts > executes the deterministic text transform with exact output`; `compiles valid code and rejects syntax without running it`; `terminates infinite loops and recovers the process`; `rejects forbidden host capabilities and invalid output shapes`; `rejects enumerable and non-enumerable custom serialization hooks`; `keeps validation intrinsics outside guest mutation`; `cancels and cleans up workers`; `retains capacity until cancelled workers terminate`; `keeps concurrent inputs isolated and throttles the fifth active run`; `proves supervisor termination after a built-in operation starts`; `keeps expected guest syntax diagnostics out of operational error logs`; `tests/database-contract.test.ts > uses bounded SELECT 1 and existing identity/shop columns without release reads or migrations`; `tests/external-preview.test.ts > reuses the same JavaScript fixture processor for tool-test and conversation execution`; `uses developmentBypass as the complete authorization signal regardless of role or staff state`; `validates canonical code content hashes and rejects stale source`; `runs JavaScript sample through the accepted code processor and receipt lifecycle`; `tests/external-tool-authoring-validation.test.ts > resolves the same explicit structured and literal bindings before real QuickJS preview`; `rejects an unsafe JavaScript request descriptor during preview`; and `tests/feature-configuration-screen.test.tsx > blocks discard navigation while a save is unresolved, then restores ordinary dirty navigation`.
- Submitted-only full-run test identities (5): `tests/discovery-process.test.ts > initializes, lists actual tools, performs an approved call, and closes`; `tests/external-tools-ui.test.tsx > stales persisted Test on argument and shop changes without persistence writes`; `tests/external-tools-ui.test.tsx > keeps an in-flight persisted Test stale after a Request edit`; `tests/external-tools-ui.test.tsx > keeps ADMIN on the Save/Validate lifecycle without publication authority`; and `tests/readiness-docker.test.ts > kills ignored-stdio descendants after leader exit on abort`.
- Run-variance check: isolated `npx vitest run tests/external-tools-ui.test.tsx` passes all 98 submitted tests; the same isolated baseline file has two 15-second timeouts in different cases. The three submitted-only full-suite External Tools UI failures therefore were not reproducible in isolation, and this task changes neither that frozen file nor Tool Authoring. The submitted full run also had one Shopify Developer MCP subprocess `EPIPE`/request-timeout (`tests/discovery-process.test.ts`) and the readiness abort-timeout delta; neither test's implementation is in task scope. No new or worsened COMMERCE-001-owned failure was found. No controller source changes were made for this evidence-only rework.
- `npm run typecheck`: passed.
- Targeted ESLint command: exit 0, 0 errors; two warnings in untouched `src/studio/code-response/code-response-panel.tsx`.
- `npm run build`: passed; includes successful manual/runtime packaging smoke checks and production build. Next emitted a Nunjucks dynamic-require warning.
- Frozen hashes: all three expected SHA-256 values matched.
- `git diff --check`: passed.

### Deviations

Attempt 2 ran both required commands on the synchronized pre-task baseline and submitted head. The frozen Studio failures are identical, the full suite has 27 fewer failing tests on the submitted head, and submitted-only External Tools UI failures do not reproduce when that file is isolated. No canonical Tool Authoring/UI owner or frozen test was changed; see the exact failure-set evidence above.

### Assumptions

The downstream controller contract is adequate for COMMERCE-002..005 based on the values/actions consumed by the retained shell and the focused behavior tests; later tasks remain consume-only as specified.

### Unresolved Issues

The six frozen `tests/studio-workspace.test.tsx` failures are inherited from pre-task commit `f9fa054b74e367fd8968fd7c26336657e945a174`; exact names and focused-run parity are recorded under Validation Results. The complete full-suite intersection, baseline-only identities, submitted-only identities, and six collection failures are recorded there as well. The submitted full run includes an MCP subprocess `EPIPE` and a readiness abort-timeout delta; the broader suite's timing-sensitive failure set differs, but no new COMMERCE-001-owned regression was reproduced. Isolated submitted `tests/external-tools-ui.test.tsx` passes 98/98.

### Architectural Concerns

No new router, command bus, state store or dependency-injection layer was introduced. No server-action signatures, persistence behavior, canonical owner files or frozen test assets were changed. Do not start `ARCH-025-COMMERCE-002` until architect review resolves the failed validation gate.

## Architect Review

### Attempt 2 Review Status

Accepted — Attempt 2

### Attempt 2 Review Notes

Attempt 2 closes both evidence-only findings from Attempt 1 without changing Commerce implementation source. The submitted `moda-interact-commerce/` tree is byte-for-byte identical to the Attempt 1 reviewed implementation at `b1f3cc6e75d9d8f78d1087cb6dcc1375801f0809`; only the parent task report changed during Attempt 2.

**A1-R1 is closed.** The report runs the exact required focused command and full `npm test` on launcher-recorded synchronized pre-task commit `f9fa054b74e367fd8968fd7c26336657e945a174` and submitted implementation `b1f3cc6e75d9d8f78d1087cb6dcc1375801f0809` under the same Node/npm/Vitest/dependency/package-lock/database-submodule environment. The six failures in frozen `tests/studio-workspace.test.tsx` are identical on both revisions. The full suite improves from 65 failed tests to 38 failed tests; 33 failing test identities and six collection failures are common to both runs, 32 failures are baseline-only, and five submitted-only failures are timing/environment variance outside COMMERCE-001 ownership. The three submitted-only External Tools UI failures pass 98/98 when the submitted frozen file is isolated; the remaining submitted-only failures are an MCP subprocess EPIPE/request-timeout and a readiness abort-timeout outside task ownership. No new or worsened COMMERCE-001-owned failure is reproduced.

This acceptance establishes durable Commerce baseline `ARCH025-COMMERCE-TEST-001` in `docs/development-baseline.md`. The baseline records only the proven stable intersection and common collection failures; it does not bless the 32 baseline-only failures or the five submitted-only run-variance failures. Later ARCH-025 Commerce tasks must still investigate any failing identity outside that durable set, and must not recreate a baseline failure that disappears.

**A1-R2 is closed.** The Completion Report records the launcher-resolved canonical workspace, dedicated parent and Commerce task worktrees, matching task branches, no shared/other-task worktree reuse, start-of-attempt parent and implementation synchronization outcomes, dependency gate, recursive submodule sync/update, exact database gitlink, Attempt 2 claim metadata/commit, submitted implementation/remote equality and final clean parent/implementation branch state.

The structural implementation remains architecture-conformant: the typed controller preserves route/load/hydration semantics, single-flight and unknown-operation reconciliation, exact operation IDs, content-revision dirty fencing and navigation-blocker asymmetries; the public `StudioWorkspace` / `StudioPage` compatibility boundary and specialized Tool/Agent Configuration early returns remain intact; source-scanner changes retain existing assertions and all frozen/adjacent owner hashes remain unchanged.

### Attempt 2 Reviewed Files

- `components/studio-workspace.tsx`
- `components/studio-workspace/studio-workspace.types.ts`
- `components/studio-workspace/use-studio-workspace-controller.ts`
- `tests/studio-workspace-controller.test.tsx`
- `tests/legacy-capability-surface.test.ts`
- `tests/arch024-preview-cleanup.test.ts`
- frozen StudioWorkspace/Agent Configuration/External Tools UI regression assets
- `docs/development-baseline.md`
- Attempt 2 Completion Report and prepared-execution evidence

### Attempt 2 Validation Reviewed

- Controller/scanner focused run: 3 files / 8 tests passed.
- Required frozen/focused comparison: baseline 6 failed / 111 passed; submitted 6 failed / 116 passed, with the same six frozen Studio failures.
- Full-suite comparison: baseline 29 failed files / 65 failed tests; submitted 23 failed files / 38 failed tests; exact identity sets and collection failures recorded.
- Submitted isolated `tests/external-tools-ui.test.tsx`: 98/98 passed.
- `npm run typecheck`: passed.
- Targeted ESLint: exit 0, no errors; two warnings only in untouched Code Response source.
- `npm run build`: passed with the existing Nunjucks dynamic-require warning.
- Frozen SHA-256 checks: passed.
- `git diff --check`: passed.

### Attempt 2 Architecture Conformance

Accepted. COMMERCE-001 is a move-only internal Commerce refactor with no server-action, persistence, authorization, cross-repository contract or product-behaviour change. Attempt 2 proves the remaining validation failures are not a COMMERCE-001 regression and makes the deterministic execution evidence durable. Under `completion_mode: automatic`, the task becomes Complete.

### Attempt 2 Dependency Reconciliation

`ARCH-025-COMMERCE-001` is Complete / Accepted at Attempt 2. Its sole enabled task, `ARCH-025-COMMERCE-002`, now has all dependencies Complete and is promoted from Pending to Ready. COMMERCE-002 is not claimed or started by this reconciliation. `ARCH025-COMMERCE-TEST-001` becomes the durable Commerce full-suite/frozen-suite no-regression reference for later ARCH-025 Commerce extraction tasks.

#### Historical Attempt 1 — Changes Requested

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
