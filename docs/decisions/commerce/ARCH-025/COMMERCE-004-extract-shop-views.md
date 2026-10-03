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
claimed_at: 2026-10-03T08:00:40Z
attempt: 1
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
- [ ] Frozen integration/state assets remain unchanged and pass. Hashes are unchanged; the six documented StudioWorkspace failures still fail.


## Validation

- [x] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/studio-workspace.test.tsx':'400ce6b68cb5a9fdeecf9233bc2b3f58a42742c974da2c5b6ffd2b5a16ae44a7','tests/agent-configuration-screen-state.test.tsx':'72c71a09eaf5bdc2d79c686cf5ec43d5abfd49cfe421cadedbbe665140582b0a','tests/external-tools-ui.test.tsx':'97ffbc70e29d4ff60a48e5aabd0ff3faec6dea7984ed0f239fcb4a8fc868f4d3'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected frozen hashes.
- [ ] `npx vitest run tests/studio-shop-views.test.tsx tests/studio-workspace.test.tsx` passes. The two new Shop-view tests pass; the six frozen StudioWorkspace tests fail with the documented baseline identities.
- [x] `git diff -- components/studio-workspace/use-studio-workspace-controller.ts components/studio-workspace/release-composer.tsx components/studio-workspace/release-detail.tsx tests/legacy-capability-surface.test.ts tests/arch024-preview-cleanup.test.ts` is empty.

- [ ] `npm test` passes without task-introduced regression. Attempt 1 completed with 30 failed files / 53 failed tests, 131 passed files / 1,333 passed tests, and 5 skipped files / 9 skipped tests. The three `tool-authoring-screen.test.tsx` timeout cases passed when rerun in isolation (34/34); other failures exceeded the durable stable baseline and remain for review.
- [x] `npm run typecheck` passes.
- [x] targeted `npm run lint -- <changed Commerce source/test files>` (or repository-equivalent targeted ESLint invocation using the declared lint script) passes (0 errors; two existing hook warnings in untouched `src/studio/code-response/code-response-panel.tsx`).
- [ ] `npm run build` succeeds. It stops in `code-runtime:smoke` with `non-string helper argument did not fail inside the guest`, before Next.js build.
- [ ] `git diff --check` passes. It reports one added blank line at EOF in `components/studio-workspace.tsx`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Commerce task.

## Implementation Notes

None

## Completion Report

### Status

Submitted for Architect review; presentation extraction is complete. Validation has the unresolved failures recorded below.

### Files Changed

- `components/studio-workspace.tsx`
- `components/studio-workspace/shop-list.tsx`
- `components/studio-workspace/shop-inspector.tsx`
- `tests/studio-shop-views.test.tsx`

### Work Completed

- Extracted the existing Shop summary list and Shop Inspector into presentation-only modules; retained copy, ordering, data display and exact Shop, Tool revision and synthetic-fixture destinations.
- Added focused tests for current list and inspector content/routes. The focused Shop-view test file passed; the combined Shop/frozen Studio command had the six documented frozen failures.
- Left the controller, Release modules, source scanners and frozen tests unchanged.

### Validation Results

- Frozen hashes matched all expected values; protected-path diff was empty.
- `npm run typecheck`: passed.
- Targeted lint: passed with zero errors and two existing warnings in untouched Code Response code.
- Isolated `tests/tool-authoring-screen.test.tsx`: 34/34 passed; its three 15-second timeouts in the full run were not reproduced in isolation.
- `npm test`: failed (30 files / 53 tests failed; 131 files / 1,333 tests passed; 5 files / 9 tests skipped). The run includes the known baseline failures plus additional failures; it is not claimed green.
- `npm run build`: failed in the packaged code-runtime smoke check before `next build`.
- `git diff --check`: failed on one added trailing blank line in `components/studio-workspace.tsx`.

### Deviations

The source extraction stayed within scope. Required repository-wide validation is non-green; failures and the whitespace warning are surfaced for Architect review rather than changed outside the task's authorized implementation surface.

### Assumptions

No Shop search, fetching, route state or Shop/Tool resolution was introduced; all are retained in their existing owners.

### Unresolved Issues

- Full-suite run has failure identities beyond the durable stable set in `ARCH025-COMMERCE-TEST-001`; see the captured Attempt 1 run and require review before treating the suite as baseline-only.
- Build smoke failure: `non-string helper argument did not fail inside the guest`.
- `git diff --check` reports an extra blank line at EOF in the modified workspace file.

### Architectural Concerns

None identified in the Shop-view extraction. Repository-wide validation issues are unrelated to the four authorized task files based on the observed failures; the full-suite additions remain unclassified beyond the isolated ToolAuthoring rerun.

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
