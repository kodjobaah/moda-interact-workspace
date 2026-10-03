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
status: review
priority: 20
executor: copilot
claimed_at: 2026-10-03T09:12:12Z
attempt: 2
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

Attempt 1 is not acceptable in its submitted state. The Shop list and Shop Inspector extraction itself is presentation-only and preserves the accepted copy, ordering, data and routes, but the exact uploaded implementation contains a task-owned regression in `components/studio-workspace.tsx` outside the intended move.

**A1-R1 — restore the `common` runtime bindings and whitespace-clean shell.**

The accepted COMMERCE-003 shell constructed:

```ts
setDirty: controller.setDirty,
runCommand: controller.runCommand,
navigate: route,
```

The submitted source instead contains TypeScript-style method declarations inside the runtime object literal:

```ts
setDirty(value: boolean): void;
runCommand(...): void;
navigate(destination: string): void;
```

A standalone TypeScript parse of the exact uploaded file reports `TS1005: ',' expected` at these lines. Restore the three accepted runtime bindings exactly, remove the task-introduced extra blank line reported by `git diff --check`, and make no unrelated StudioWorkspace changes.

After this correction, rerun the required `npm run typecheck` and `git diff --check` against the exact committed Attempt 2 source. The Completion Report must record results that correspond to the reviewed source revision.

**A1-R2 — close the required production-build gate without changing unrelated code-runtime behavior.**

`npm run build` is a required task gate and is currently unchecked because the packaged code-runtime smoke stops at `non-string helper argument did not fail inside the guest`. Rerun the build after A1-R1.

If the build succeeds, record the passing result. If the same smoke failure remains, compare the identical build/smoke command on the launcher-recorded synchronized pre-task Commerce revision and the corrected submitted revision under the same environment. If it is proven pre-existing and unrelated to the four authorised COMMERCE-004 files, record that deterministic evidence and return it to `moda_architect`; do not modify unrelated code-runtime implementation merely to make this extraction task green.

**A1-R3 — classify the full-suite failure identities against `ARCH025-COMMERCE-TEST-001`.**

The submitted report gives only aggregate full-suite counts (53 failed tests) plus an isolated ToolAuthoring rerun. The durable baseline permits later ARCH-025 Commerce tasks to reuse only the stable named test/collection identities with equivalent reasons. Record every failing test identity and collection failure from the corrected Attempt 2 full run and classify it against `ARCH025-COMMERCE-TEST-001`.

For every new, changed or worsened identity, investigate it as a possible task regression. An isolated rerun may establish run variance where appropriate, but do not add new failures to the baseline or treat improved totals as sufficient evidence. If a task-owned regression is demonstrated, correct only that regression and rerun the required validation.

**A1-R4 — record the deterministic prepared-execution packet.**

The Completion Report does not currently contain the launcher-resolved physical-isolation/start-of-attempt packet required for review. Attempt 2 must record the canonical workspace root; dedicated parent and Commerce task worktrees/branches; start-of-attempt parent and implementation synchronization / `origin/main` incorporation evidence; COMMERCE-003 dependency gate; recursive submodule sync/update and exact Database gitlink; Attempt 2 claim metadata and durable claim commit; final implementation and parent report heads with matching remote task heads; and final clean status for both worktrees.

A matching launcher packet is sufficient. Do not rerun preparation merely to reproduce discovery steps, and do not create implementation churn solely for evidence.

The next attempt remains scoped to COMMERCE-004. Do not start COMMERCE-005.

### Reviewed Files

- `components/studio-workspace.tsx`
- `components/studio-workspace/shop-list.tsx`
- `components/studio-workspace/shop-inspector.tsx`
- `tests/studio-shop-views.test.tsx`
- `docs/development-baseline.md`
- `docs/decisions/commerce/ARCH-025/COMMERCE-004-extract-shop-views.md`
- accepted COMMERCE-003 `components/studio-workspace.tsx` comparison

### Validation Reviewed

- Frozen SHA-256 evidence: unchanged.
- Protected controller / Release / accepted source-scanner diff: unchanged.
- Focused Shop-view tests: reported passing.
- Frozen StudioWorkspace failures: reported as the six documented `ARCH025-COMMERCE-TEST-001` failures.
- Exact uploaded `components/studio-workspace.tsx`: standalone TypeScript parse reproduces `TS1005` syntax errors at the corrupted `common` bindings.
- `npm test`: submitted non-green result is not fully classified against the durable baseline.
- `npm run build`: submitted required gate is non-green at packaged code-runtime smoke.
- `git diff --check`: submitted required gate is non-green on the task-modified StudioWorkspace file.

### Architecture Conformance

The extracted Shop presentation modules themselves conform to R1-R3 and preserve the accepted Shop list/Inspector content and routes. The submitted StudioWorkspace shell does not conform to the move-only/common-invariant contract because it corrupts the existing controller bindings. Required validation/evidence is also incomplete, so the task cannot be accepted yet.

### Follow-up

Return the same task through the normal `/moda-task ARCH-025-COMMERCE-004` path. Attempt 2 must satisfy A1-R1 through A1-R4, set all genuinely satisfied Acceptance Criteria / Validation checkboxes consistently, finish the Completion Report, return to `review`, and STOP. `ARCH-025-COMMERCE-005` remains gated.
