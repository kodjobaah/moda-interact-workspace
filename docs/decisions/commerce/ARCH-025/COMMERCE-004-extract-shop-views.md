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
status: in_progress
priority: 20
executor: copilot
claimed_at: 2026-10-03T10:00:22Z
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
- [ ] Frozen integration/state assets remain unchanged and pass. Hashes are unchanged; the six StudioWorkspace failures match the documented baseline identities.


## Validation

- [x] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/studio-workspace.test.tsx':'400ce6b68cb5a9fdeecf9233bc2b3f58a42742c974da2c5b6ffd2b5a16ae44a7','tests/agent-configuration-screen-state.test.tsx':'72c71a09eaf5bdc2d79c686cf5ec43d5abfd49cfe421cadedbbe665140582b0a','tests/external-tools-ui.test.tsx':'97ffbc70e29d4ff60a48e5aabd0ff3faec6dea7984ed0f239fcb4a8fc868f4d3'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected frozen hashes.
- [ ] `npx vitest run tests/studio-shop-views.test.tsx tests/studio-workspace.test.tsx` passes. Attempt 2: the two new Shop-view tests passed and the six frozen StudioWorkspace failures match the documented baseline identities.
- [x] `git diff -- components/studio-workspace/use-studio-workspace-controller.ts components/studio-workspace/release-composer.tsx components/studio-workspace/release-detail.tsx tests/legacy-capability-surface.test.ts tests/arch024-preview-cleanup.test.ts` is empty.

- [ ] `npm test` passes without task-introduced regression. Attempt 2 completed with 25 failed files / 43 failed tests, 136 passed files / 1,343 passed tests, and 5 skipped files / 9 skipped tests. Exactly 33 failures match the stable set in `ARCH025-COMMERCE-TEST-001`; the six collection failures also match. The 10 additional identities listed in the Completion Report all passed when their containing files were rerun in isolation.
- [x] `npm run typecheck` passes.
- [x] targeted `npm run lint -- <changed Commerce source/test files>` (or repository-equivalent targeted ESLint invocation using the declared lint script) passes (0 errors; two existing hook warnings in untouched `src/studio/code-response/code-response-panel.tsx`).
- [ ] `npm run build` succeeds. Corrected Attempt 2 stops in `code-runtime:smoke` with `packaged v2 helper output mismatch`; the identical smoke stage passes on the pre-task source snapshot under the same pinned Node/dependency environment. No code-runtime source/config delta exists between the revisions; see the Completion Report for exact evidence and the unresolved build discrepancy.
- [x] `git diff --check` passes on corrected Attempt 2.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Commerce task.

## Implementation Notes

None

## Completion Report

### Status

Attempt 2 corrections submitted for Architect review. The Shop extraction is complete; repository-wide build validation remains unresolved and is explicitly reported below.

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
- `npm run build`: corrected Attempt 2 fails in `code-runtime:smoke` before Prisma generation and Next.js build with `packaged v2 helper output mismatch`. In a `git archive` snapshot of synchronized pre-task `origin/main` (`494e8ae069923f41db7578cf2ee4f48240c69252`), using the same pinned Node and linked installed dependencies, `npm run code-runtime:package && npm run code-runtime:smoke` passed. The full baseline `npm run build` then stopped at `prisma:generate` because the archive has no `.git` metadata. The helper artifact hashes differ (`83fe8b710c646680781e605baa64f77ef215cea9bd7aa7df4133afd358c9c31a` submitted vs `2627adfc3c15d7ba53501c9e40eff18228c3472bbac4e250303d662a4675f579` baseline), despite no code-runtime source/config/package diff between `origin/main` and the task branch. This does not prove a pre-existing build failure; it remains an unresolved build/environment discrepancy for Architect disposition. No unrelated code-runtime files were changed.

### Prepared Execution Packet

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Dedicated parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-COMMERCE-004`, `task/ARCH-025-COMMERCE-004`. At start, launcher reported task-branch fast-forward `not-needed`, `origin/main` incorporated `yes`, head `c2fa8a576569ab10ec6b4c1f341daa6a46af753d`.
- Dedicated Commerce worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-COMMERCE-004`, `task/ARCH-025-COMMERCE-004`. At start, launcher reported task-branch fast-forward `not-needed`, `origin/main` incorporated `already-current`, head `3b8c454661bedc7f92512e31dfb87243e7414ef0`.
- Dependency gate: `ARCH-025-COMMERCE-003` complete; gate passed.
- Recursive submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; Database gitlink `cfeeb12456b4e05067a96857a8c47837d7e33bbd` initialized and ready.
- Attempt 2 claim: executor `copilot`, claimed `2026-10-03T09:12:12Z`, parent claim commit `d2872009f9b8f342e674cb22e7bb222792947ef9`, committed and pushed. Final parent synchronization reported task-branch fast-forward `not-needed`, `origin/main` `already-current`, head `c2fa8a576569ab10ec6b4c1f341daa6a46af753d`.
- Final implementation commit: `75aff7193d78c4b5ccac585d3818bfc298f872da`, pushed to `origin/task/ARCH-025-COMMERCE-004`; local and remote heads matched and implementation worktree was clean at verification.
- Parent report branch: `task/ARCH-025-COMMERCE-004`; final report commit is pushed and local/remote heads and clean status are verified at submission. The exact published report head is included in the handoff summary.

### Deviations

The source extraction and A1-R1 correction stayed within scope. The full suite is non-green but its additional failure identities pass in isolation; the required build smoke differs from the pre-task snapshot and remains unresolved. No unrelated implementation was changed.

### Assumptions

No Shop search, fetching, route state or Shop/Tool resolution was introduced; all are retained in their existing owners.

### Unresolved Issues

- Required `npm run build` fails in packaged code-runtime smoke on the task tree, while the same package/smoke stage passes on synchronized pre-task source. Input source/config/package diffs are empty; generated helper hashes differ. This discrepancy is unresolved and requires Architect disposition.
- Full `npm test` is non-green, with 33 exact stable baseline failures, six exact baseline collection failures, and 10 additional identities that all passed in isolation as recorded above.

### Architectural Concerns

None identified in the Shop-view extraction or corrected runtime bindings. The packaged runtime build discrepancy is outside the authorized task surface and is submitted with comparison evidence for Architect disposition.

## Architect Review

### Review Status

Changes Requested

### Review Notes

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

- A1-R1 corrected source: accepted controller bindings restored; current source diff against COMMERCE-003 is limited to the Shop-view extraction plus whitespace cleanup.
- Frozen SHA-256 evidence: unchanged.
- Protected controller / Release / accepted source-scanner diff: unchanged.
- Focused Shop-view tests: passed.
- Frozen StudioWorkspace failures: six exact `ARCH025-COMMERCE-TEST-001` identities.
- Full `npm test`: 33 exact stable failures plus six exact baseline collection failures; 10 additional identities all pass isolated containing-file reruns and are not added to the baseline.
- `npm run typecheck`: passed.
- Targeted lint: passed with only existing warnings in untouched Code Response code.
- `git diff --check`: passed.
- Launcher/worktree packet: present and sufficient.
- `npm run build`: **not satisfied**; task tree fails at packaged code-runtime smoke while synchronized pre-task package/smoke passes. The generated-helper discrepancy remains unresolved.

### Architecture Conformance

The Shop list and Shop Inspector extraction conforms to the intended presentation-only boundary, and the Attempt 1 controller corruption is corrected. No task-owned full-suite regression has been demonstrated. Architecture conformance is therefore blocked only by the unresolved required build/reproducibility gate; acceptance is withheld until that gate is closed or the task is formally blocked for an out-of-scope code-runtime issue.

### Follow-up

Return the same task through `/moda-task ARCH-025-COMMERCE-004`. Attempt 3 is primarily a deterministic build-artifact/reproducibility investigation. Do not redesign the Shop views and do not modify unrelated code-runtime behavior. If the clean committed C004 tree can pass the required build, record the evidence, finish the task-owned checkboxes/Completion Report, return to `review`, and STOP. If the clean C004 tree deterministically fails while the clean pre-task tree passes with identical packaging inputs, return the task `blocked` with the captured artifact evidence rather than changing out-of-scope runtime code. `ARCH-025-COMMERCE-005` remains gated.
