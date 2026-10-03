---
id: ARCH-025-COMMERCE-004
architecture_id: ARCH-025
title: Extract Studio Shop list and Shop Inspector views
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
attempt: 3
depends_on:
  - ARCH-025-COMMERCE-003
enables:
  - ARCH-025-COMMERCE-005
created: 2026-10-02
updated: 2026-10-03
---

# Extract Studio Shop list and Shop Inspector views

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the existing Shop summary list and Shop Inspector into bounded presentation modules without adding search, I/O or changing accepted Shop/Tool navigation.

## Context

The current Shops page/detail views are small and cohesive but unrelated to global workspace orchestration or Release workflows. They can move together as one independently reviewable presentation capability.

## Scope

Authorised implementation surface:

```text
components/studio-workspace.tsx
components/studio-workspace/shop-list.tsx
components/studio-workspace/shop-inspector.tsx
tests/studio-shop-views.test.tsx
```

## Out of Scope

New Shop search, server-action changes, Shop execution/eligibility changes, Tool detail changes, controller/release changes, generic page-router extraction.

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

### R1 — current Shop list only

Extract the current Shops list presentation to `shop-list.tsx`. Preserve the existing heading/copy, current list order/data, label/domain/plan display and `/shops/<id>` inspection links. Do not add Shop search merely because the copy mentions search; `listShops("")` behaviour remains controller/server-action owned.

### R2 — Shop Inspector

Move `ShopInspector` unchanged into `shop-inspector.tsx`: Plan, Active release, eligibility rows, exact descriptor details/input schema, exact Tool revision link, three-step CommerceAgent tool-list explanation and the current final link/text/destination. Do not modernise the current `/preview?shop=<id>&return=/shops/<id>` link or its `Test with synthetic fixtures` label as part of this move-only task.

### R3 — bounded presentation

These modules are presentation only. They must not call server actions, fetch new Shop data, own route state or duplicate Tool/eligibility resolution.


## Work Items

- [x] Extract Shop list presentation.
- [x] Extract Shop Inspector presentation.
- [x] Add focused Shop-view tests for current labels/routes/content.
- [x] Keep controller and both Release modules unchanged.


## Interfaces / Contracts

Presentation-only repository-internal props derived from existing `ShopSummary` / `ShopDetail` contracts.

## Dependencies

- `ARCH-025-COMMERCE-003`

## Enables

- `ARCH-025-COMMERCE-005`

## Acceptance Criteria

- [x] Shops list and detail render the same accepted information/routes with no new search or I/O.
- [x] Tool revision and current synthetic-fixture link destinations remain exact.
- [x] Frozen integration/state assets remain unchanged and pass. Hashes are unchanged; the six StudioWorkspace failures match the documented baseline identities.


## Validation

- [x] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/studio-workspace.test.tsx':'400ce6b68cb5a9fdeecf9233bc2b3f58a42742c974da2c5b6ffd2b5a16ae44a7','tests/agent-configuration-screen-state.test.tsx':'72c71a09eaf5bdc2d79c686cf5ec43d5abfd49cfe421cadedbbe665140582b0a','tests/external-tools-ui.test.tsx':'97ffbc70e29d4ff60a48e5aabd0ff3faec6dea7984ed0f239fcb4a8fc868f4d3'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected frozen hashes.
- [x] `npx vitest run tests/studio-shop-views.test.tsx tests/studio-workspace.test.tsx` has no task-introduced regression. Attempt 2: both Shop-view tests passed and the six frozen StudioWorkspace failures match the documented baseline identities.
- [x] `git diff -- components/studio-workspace/use-studio-workspace-controller.ts components/studio-workspace/release-composer.tsx components/studio-workspace/release-detail.tsx tests/legacy-capability-surface.test.ts tests/arch024-preview-cleanup.test.ts` is empty.

- [x] `npm test` completes without task-introduced regression under the accepted baseline. Attempt 2 completed with 25 failed files / 43 failed tests, 136 passed files / 1,343 passed tests, and 5 skipped files / 9 skipped tests. Exactly 33 failures match the stable set in `ARCH025-COMMERCE-TEST-001`; the six collection failures also match. The 10 additional identities listed in the Completion Report all passed when their containing files were rerun in isolation.
- [x] `npm run typecheck` passes.
- [x] targeted `npm run lint -- <changed Commerce source/test files>` (or repository-equivalent targeted ESLint invocation using the declared lint script) passes (0 errors; two existing hook warnings in untouched `src/studio/code-response/code-response-panel.tsx`).
- [x] `npm run build` succeeds. Attempt 3 completed on the exact C004 commit with exit code 0; packaged-runtime artifact/smoke variability is documented in the Completion Report.
- [x] `git diff --check` passes on corrected Attempt 2.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Commerce task.

## Implementation Notes

None

## Completion Report

### Status

Attempt 3 submitted for Architect review. The Shop extraction and required validation gates are complete; A2-R1 reproducibility evidence is recorded below.

### Files Changed

- `components/studio-workspace.tsx`
- `components/studio-workspace/shop-list.tsx`
- `components/studio-workspace/shop-inspector.tsx`
- `tests/studio-shop-views.test.tsx`

### Work Completed

- Extracted the existing Shop summary list and Shop Inspector into presentation-only modules; retained copy, ordering, data display and exact Shop, Tool revision and synthetic-fixture destinations.
- Restored the accepted `setDirty: controller.setDirty`, `runCommand: controller.runCommand` and `navigate: route` runtime bindings in `common`, and removed the extra EOF blank line identified by A1-R1.
- Added focused tests for current list and inspector content/routes. Both Shop-view tests passed; the combined Shop/frozen Studio command had the six documented frozen failures.
- Left the controller, Release modules, source scanners and frozen tests unchanged.

### Validation Results

- Frozen hashes matched all expected values; protected-path diff was empty; final `git diff --check` passed.
- `npm run typecheck`: passed on corrected Attempt 2.
- Targeted lint: passed with zero errors and two existing warnings in untouched `src/studio/code-response/code-response-panel.tsx`.
- Focused Shop/frozen Studio command: 9 passed and 6 failed. The two Shop-view tests passed; all six Studio failures match the frozen baseline identities in `ARCH025-COMMERCE-TEST-001`.
- `npm test`: 25 failed files / 43 failed tests, 136 passed files / 1,343 passed tests, 5 skipped files / 9 skipped tests. Of 43 failures, 33 match the stable baseline identities exactly and with equivalent failures. The other 10 identities, all outside the task-owned files, were:
  - `tests/code-runtime-proof.test.ts` — `proves supervisor termination after a built-in operation starts`.
  - `tests/readiness-docker.test.ts` — `kills ignored-stdio descendants after leader exit on abort` (the separate timeout identity is baseline-covered).
  - `tests/shop-execution-context.test.ts` — `lists and resolves server-derived shop metadata without exposing an offline token`.
  - `tests/external-tools-ui.test.tsx` — `preserves independent request mode drafts and round-trips typed canonical JavaScript bindings`; `authors and derives a nested Visual list without persisting browser field ids`; `runs the exact local External HTTP candidate with ephemeral arguments and selected shop`; `stales persisted Test on argument and shop changes without persistence writes`.
  - `tests/tool-authoring-screen.test.tsx` — `runs a New Tool live test against its current candidate without persisting it`; `submits current local External HTTP edits through the atomic action`; `keeps independent declarative and JavaScript request drafts in new-tool authoring`.
- Each containing file for those 10 additional failures passed in isolation: code-runtime proof 12/12, readiness Docker 10/10, Shop execution context 5/5, External Tools UI 98/98, ToolAuthoring screen 34/34. These are classified as suite-load/run-variance failures, not as additions to the durable baseline.
- All six collection failures match the baseline: `tests/agent-configuration-model-postgres.test.ts`, `tests/agent-configuration-prompts-postgres.test.ts`, `tests/c20-integration-fixture.test.ts`, `tests/local-external-mcp-diagnostic.test.ts`, `tests/preview-openrouter-postgres.test.ts`, and `tests/studio-integration-c20.test.ts`.
- Attempt 2's `npm run build` stopped in `code-runtime:smoke` with `packaged v2 helper output mismatch`; that attempt did not establish a pre-existing failure. Attempt 3 performed the A2-R1 comparison below and subsequently completed the required full build successfully.
- Attempt 3 A2-R1 reproducibility investigation: two `code-runtime:package` runs on the dedicated C004 worktree generated identical files (helper `83fe8b710c646680781e605baa64f77ef215cea9bd7aa7df4133afd358c9c31a`, manifest `57e71653c06592e3e322eb03b1038bc112cff05af8fae3939b041671fd27d7c4`, WASM `d4c9375f2b1ca4dc95f72c8aa2982a7a9951ac8011490d79c6582df732b4bbd9`, worker `ee4612d9ab534b24889c1bfb641171d1ada8c9d4e66fad7baf15497e538f604a`). Their smoke executions respectively passed and failed with `packaged transform output mismatch`.
- Clean snapshots of pre-task `494e8ae069923f41db7578cf2ee4f48240c69252` and C004 `75aff7193d78c4b5ccac585d3818bfc298f872da`, linked to the same installed dependencies, had identical hashes for all declared packaging inputs. Both packaged the same helper (`96ca33d212a09383d7c68bb6dcafbbc3668e56288acf134df86933e13d1c4f1`), manifest (`f4f418ecc371d0866afa40247a2f0848c07ae7a93ff31e49485b08311d13b806`), WASM and worker. The pre-task smoke passed; clean C004 smoke failed once with `packaged v2 helper output mismatch`. Cross-running preserved worktree and snapshot artifacts against both snapshots passed all four combinations.
- The worktree helper hash difference is confined to esbuild source-path comments: after removing comment-only lines, the bundles have zero differing lines. Resolved inputs were Node `v24.19.0`, `string-strip-html@13.6.2` (source SHA-256 `4cbd20b2047a53b8f4f06913ac60a6777f33ac8c4d4a8d0b63993d6b155bba0e`), `esbuild@0.28.2` and its darwin/x64 native binary (SHA-256 `7fe5c9c905fff0a05d92db98929434ab4d3b6dd92d7a7688922db74380c75df3`). The declared source, packaging scripts, manifest inputs and package files match between snapshots.
- Required full `npm run build` on the exact C004 worktree subsequently completed with explicit `build_exit=0`. Its packaged-runtime smoke passed, Prisma Client generation completed, Next.js compilation and TypeScript passed, static pages were generated, and the production route table was emitted. No runtime or dependency files were changed. The standalone smoke variability did not reproduce as a deterministic C004-only failure and did not prevent the required full build from passing.

### Prepared Execution Packet

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Dedicated parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-COMMERCE-004`, `task/ARCH-025-COMMERCE-004`. At start, launcher reported task-branch fast-forward `not-needed`, `origin/main` incorporated `yes`, head `c2fa8a576569ab10ec6b4c1f341daa6a46af753d`.
- Dedicated Commerce worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-COMMERCE-004`, `task/ARCH-025-COMMERCE-004`. At start, launcher reported task-branch fast-forward `not-needed`, `origin/main` incorporated `already-current`, head `3b8c454661bedc7f92512e31dfb87243e7414ef0`.
- Dependency gate: `ARCH-025-COMMERCE-003` complete; gate passed.
- Recursive submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; Database gitlink `cfeeb12456b4e05067a96857a8c47837d7e33bbd` initialized and ready.
- Attempt 2 claim: executor `copilot`, claimed `2026-10-03T09:12:12Z`, parent claim commit `d2872009f9b8f342e674cb22e7bb222792947ef9`, committed and pushed. Final parent synchronization reported task-branch fast-forward `not-needed`, `origin/main` `already-current`, head `c2fa8a576569ab10ec6b4c1f341daa6a46af753d`.
- Final implementation commit: `75aff7193d78c4b5ccac585d3818bfc298f872da`, pushed to `origin/task/ARCH-025-COMMERCE-004`; local and remote heads matched and implementation worktree was clean at verification.
- Attempt 3 claim: executor `copilot`, claimed `2026-10-03T10:00:22Z`, parent claim commit `776949ac0d4f40bff74ae13d16a3f9b2d4430fd2`, committed and pushed. The Attempt 3 parent start head was `5cab6f78985a63268d49af115ff71b4bcdd92547`; implementation start/final head is `75aff7193d78c4b5ccac585d3818bfc298f872da`.
- Parent report branch: `task/ARCH-025-COMMERCE-004`; Attempt 3 report commit is pushed and local/remote heads and clean status are verified at submission. The exact published report head is included in the handoff summary.

### Deviations

The source extraction and A1-R1 correction stayed within scope. The full suite is non-green under the accepted baseline classification. Attempt 3 confirmed the required production build succeeds while documenting intermittent standalone smoke outcomes and showing that the helper bundle differences are path comments, not executable content. No unrelated implementation was changed.

### Assumptions

No Shop search, fetching, route state or Shop/Tool resolution was introduced; all are retained in their existing owners.

### Unresolved Issues

- None affecting the task acceptance gates. The standalone packaged-runtime smoke variability is documented under Validation Results for Architect review; the required full build completed successfully.
- Full `npm test` is non-green, with 33 exact stable baseline failures, six exact baseline collection failures, and 10 additional identities that all passed in isolation as recorded above.

### Architectural Concerns

None identified in the Shop-view extraction or corrected runtime bindings. The packaged runtime build discrepancy is outside the authorized task surface and is submitted with comparison evidence for Architect disposition.

## Architect Review

### Review Status

Accepted

### Review Notes

**Attempt 3 — Accepted**

A2-R1 is closed. The required `npm run build` completed on the exact committed C004 implementation `75aff7193d78c4b5ccac585d3818bfc298f872da` with explicit exit code 0. Prisma Client generation, packaged code-runtime smoke, Next.js compilation, TypeScript, static-page generation and production route emission all completed without any C004 source/package/dependency change.

The standalone code-runtime smoke investigation does not establish a deterministic C004 regression. Repeated worktree packaging produced identical helper/manifest/WASM/worker hashes while one standalone smoke passed and one failed. Clean pre-task and exact-C004 snapshots had identical declared packaging inputs and executable helper content; all preserved-artifact cross-runs passed. The observed helper-text difference was confined to esbuild source-path comments, not executable bundle content. The failure therefore did not follow the C004 revision, a distinct artifact, or semantic helper content, and it no longer blocks the required production build.

A1-R1, A1-R3 and A1-R4 remain closed from Attempt 2. The Shop list / Shop Inspector extraction remains a presentation-only move, the accepted runtime bindings are restored, `git diff --check` is clean, and the broad-suite evidence remains bounded by `ARCH025-COMMERCE-TEST-001`: 33 exact stable failures plus six exact collection failures recur, while the ten additional full-run identities each pass their isolated file rerun and are not added to the durable baseline.

No code-runtime, package, dependency or unrelated runtime implementation was changed during Attempt 3. COMMERCE-004 therefore satisfies its Work Items, Acceptance Criteria and required Validation.

**Attempt 2 re-review**

A1-R1, A1-R3 and A1-R4 are closed. The corrected `StudioWorkspace` restores the accepted `setDirty: controller.setDirty`, `runCommand: controller.runCommand` and `navigate: route` runtime bindings; `git diff --check`, typecheck and targeted lint are now clean. The full-suite report classifies the 33 durable `ARCH025-COMMERCE-TEST-001` failures and six collection failures exactly, and each of the 10 additional out-of-baseline identities passes its isolated file rerun. The Completion Report also records the required dedicated-worktree, synchronization, dependency, recursive-submodule, claim and final remote-alignment evidence.

The Shop-list / Shop-Inspector extraction itself remains a faithful presentation-only move. Direct comparison with the accepted COMMERCE-003 source shows that the only production changes are removal of the local Shop renderers, import of `ShopList` / `ShopInspector`, and the A1-R1 restoration. The controller, Release modules, code-runtime sources/configuration, package manifests and lockfile remain unchanged.

**A2-R1 — the required production-build gate remains unresolved.**

`npm run build` is a required COMMERCE-004 validation gate and still fails in `code-runtime:smoke` with `packaged v2 helper output mismatch`. The synchronized pre-task source snapshot passes the identical `code-runtime:package && code-runtime:smoke` stage under the same pinned Node/dependency environment. Therefore the failure has **not** been proven pre-existing or baseline-equivalent, and COMMERCE-004 cannot be accepted while the build checkbox remains knowingly incomplete.

The current evidence does strongly suggest a generated-artifact/environment discrepancy rather than Shop-view source behavior:

- there is no diff in `src/commerce/code-runtime/**`, `scripts/code-runtime-manifest.mjs`, `scripts/code-runtime-packaged-smoke.mjs`, `package.json` or `package-lock.json`;
- the submitted tree's `docs/code-runtime-proof.md` records helper SHA-256 `83fe8b710c646680781e605baa64f77ef215cea9bd7aa7df4133afd358c9c31a` as an accepted passing packaged helper, while the Attempt 2 task run reports that same helper hash on the failing task artifact;
- the pre-task comparison generated a different helper hash (`2627adfc3c15d7ba53501c9e40eff18228c3472bbac4e250303d662a4675f579`) and passed the smoke.

Attempt 3 must investigate this deterministically **without changing unrelated code-runtime production behavior**:

1. Reproduce `npm run code-runtime:package && npm run code-runtime:smoke` at least twice on the exact committed C004 head in the dedicated task worktree and record the helper/manifest/WASM/worker hashes and exact smoke result for each run.
2. Create clean source snapshots of both the launcher-recorded synchronized pre-task commit and the exact C004 head (for example with `git archive`), attach the same pinned dependency tree/environment to both, and run the identical package/smoke pair on both. This comparison does not require Prisma or a full Next build.
3. Hash every packaging input that can affect the helper: `helpers-v2-entry.js`, `helper-injected-globals.js`, `worker.mjs`, `scripts/code-runtime-manifest.mjs`, `scripts/code-runtime-packaged-smoke.mjs`, `package.json`, `package-lock.json`, the resolved `string-strip-html` package source/version and the resolved `esbuild` version/binary. Record any difference.
4. If generated `helpers-v2.js` differs between revisions/runs while the declared inputs are identical, preserve both artifacts and record a textual/binary diff sufficient to identify whether the difference is path/environment metadata or semantic bundle content.
5. Cross-check the generated artifacts: run the packaged smoke against each preserved artifact under the same environment. Record whether the failure follows the generated artifact or the source checkout.
6. If the exact C004 commit passes package/smoke from a clean snapshot and the dedicated task worktree failure is attributable to stale/local generated state, restore the task worktree to a clean reproducible state and rerun the complete required `npm run build`.
7. If the exact clean C004 commit still fails while the exact clean pre-task commit passes despite identical declared packaging inputs, stop without editing code-runtime source and return the task **blocked** to `moda_architect` with the artifact/input evidence. The architect will then decide whether a separate bounded code-runtime reproducibility/correction task is required.

Do not add this unresolved condition to `ARCH025-COMMERCE-TEST-001`; that baseline explicitly does not substitute for the production build gate. Do not modify code-runtime, package/dependency or unrelated runtime files inside COMMERCE-004 merely to force a green build.

Before resubmission, reconcile the task-owned checkboxes consistently: the frozen/focused and full-suite no-regression criteria may be checked as satisfied under the accepted baseline evidence, but `npm run build` must remain unchecked until it actually passes or the task is returned `blocked` for architect disposition.

The next attempt remains scoped to COMMERCE-004. Do not start COMMERCE-005.

**Attempt 1 review history**

Attempt 1 found the Shop extraction itself presentation-only but identified corrupted `common` runtime bindings, non-green required build/whitespace gates, incomplete full-suite classification and missing launcher evidence. Those findings are retained below as historical context; A1-R1, A1-R3 and A1-R4 are now closed by Attempt 2.

### Reviewed Files

- `components/studio-workspace.tsx`
- `components/studio-workspace/shop-list.tsx`
- `components/studio-workspace/shop-inspector.tsx`
- `tests/studio-shop-views.test.tsx`
- `src/commerce/code-runtime/**`
- `scripts/code-runtime-manifest.mjs`
- `scripts/code-runtime-packaged-smoke.mjs`
- `docs/code-runtime-proof.md`
- `package.json`
- `package-lock.json`
- `docs/development-baseline.md`
- `docs/decisions/commerce/ARCH-025/COMMERCE-004-extract-shop-views.md`
- accepted COMMERCE-003 `moda-interact-commerce/` comparison

### Validation Reviewed

- Accepted controller bindings remain restored: `setDirty: controller.setDirty`, `runCommand: controller.runCommand`, `navigate: route`.
- Frozen SHA-256 evidence: unchanged.
- Protected controller / Release / accepted source-scanner diff: unchanged.
- Focused Shop-view tests: passed.
- Frozen StudioWorkspace failures: six exact `ARCH025-COMMERCE-TEST-001` identities.
- Full `npm test`: 33 exact stable failures plus six exact baseline collection failures; ten additional identities all pass isolated containing-file reruns and are not added to the baseline.
- `npm run typecheck`: passed.
- Targeted lint: passed with only existing warnings in untouched Code Response code.
- `git diff --check`: passed.
- Launcher/worktree packet: present and sufficient for Attempts 2 and 3.
- Attempt 3 standalone package/smoke investigation: packaging hashes and executable helper content are stable across the compared clean snapshots; all preserved-artifact cross-runs passed; isolated smoke outcomes were intermittent rather than revision-bound.
- Required full `npm run build` on exact C004 commit `75aff7193d78c4b5ccac585d3818bfc298f872da`: passed with exit code 0.

### Architecture Conformance

Conformant. The Shop list and Shop Inspector are bounded presentation owners with existing data, copy, ordering and routes preserved. The accepted `StudioWorkspace` controller/runtime bindings remain intact; controller, Release modules, source scanners, code-runtime implementation and package/dependency state are unchanged. No task-owned full-suite regression has been demonstrated, and the required production build is now green on the exact submitted implementation.

The intermittent standalone packaged-runtime smoke observations are retained as non-blocking diagnostic evidence only. They are not added to `ARCH025-COMMERCE-TEST-001` and do not authorize unrelated runtime changes.

### Follow-up

COMMERCE-004 is architect-accepted Complete at Attempt 3. Promote `ARCH-025-COMMERCE-005` to Ready; do not claim or start it as part of this review. Preserve `ARCH025-COMMERCE-TEST-001` without expansion from the intermittent standalone smoke or isolated full-suite outliers.
