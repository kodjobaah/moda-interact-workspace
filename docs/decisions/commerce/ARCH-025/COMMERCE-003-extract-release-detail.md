---
id: ARCH-025-COMMERCE-003
architecture_id: ARCH-025
title: Extract Release Detail clone activation and rollback view
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
claimed_at: 2026-10-03T01:54:13Z
attempt: 2
depends_on:
  - ARCH-025-COMMERCE-002
enables:
  - ARCH-025-COMMERCE-004
created: 2026-10-02
updated: 2026-10-03
---

# Extract Release Detail clone activation and rollback view

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract Release Detail clone-as-new, activation and rollback presentation into a dedicated module while preserving Studio composer handoff, role gating and active-pointer fencing.

## Context

After COMMERCE-002, Release Detail remains a separate workflow with different state/failure semantics from composition: clone handoff, privileged activation/rollback confirmation and active-pointer CAS fencing.

## Scope

Authorised implementation surface:

```text
components/studio-workspace.tsx
components/studio-workspace/release-detail.tsx
tests/release-detail.test.tsx
```

## Out of Scope

Controller or Release Composer redesign, release server-action changes, response-contract schema changes, Shop/page routing extraction.

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

### R1 — Release Detail ownership

Move the complete current `ReleaseDetail` presentation/workflow into `components/studio-workspace/release-detail.tsx`. Local confirmation/reason state remains local.

### R2 — edit-as-new handoff

Preserve the current role-independent **Edit as new release** affordance exactly; it remains available before the SUPER_ADMIN activation/rollback gate, including for `ADMIN`. Preserve `composer.setRelease(...)` exactly: a newly generated Studio operation/handoff ID using the accepted COMMERCE-001 helper, exact members, `structuredClone(responseContract)`, existing validation hash, blank reason and return route `/releases/<id>?tab=response-contract`; then navigate to `/releases?cloneResponseFrom=<id>`.

### R3 — activation/rollback role and fence

Preserve SUPER_ADMIN gating, ADMIN explanatory copy, previous-release rollback label, confirmation dialog, non-empty reason requirement, current active-pointer version fence, exact activate/rollback server-action payloads and current success/reload behaviour through `runCommand`.

### R4 — current dirty/cancel quirk

Typing the confirmation reason continues to mark global dirty. Cancelling the dialog currently only closes confirmation and does not clear global dirty; preserve that behaviour during extraction rather than silently normalising it.


## Work Items

- [x] Move Release Detail into the dedicated module.
- [x] Reuse the accepted internal operation-ID helper and workspace command/navigation contract.
- [x] Add focused clone/role/fence/dirty-confirmation tests.
- [x] Keep COMMERCE-001 controller and COMMERCE-002 Release Composer unchanged.


## Interfaces / Contracts

Consumes accepted COMMERCE-001 common props plus `useStudioComposer`; no new public contract.

## Dependencies

- `ARCH-025-COMMERCE-002`

## Enables

- `ARCH-025-COMMERCE-004`

## Acceptance Criteria

- [x] Edit-as-new remains role-independent and its handoff shape/destinations are unchanged.
- [x] Activation/rollback role gating, confirmation and active-pointer fencing are unchanged.
- [x] Current dirty-on-reason / cancel-does-not-clear-dirty behaviour is preserved.
- [ ] Frozen 13/3/90-test assets remain unchanged and pass. The assets are byte-identical; the six known StudioWorkspace failures remain as documented in `ARCH025-COMMERCE-TEST-001`.


## Validation

- [ ] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/studio-workspace.test.tsx':'400ce6b68cb5a9fdeecf9233bc2b3f58a42742c974da2c5b6ffd2b5a16ae44a7','tests/agent-configuration-screen-state.test.tsx':'72c71a09eaf5bdc2d79c686cf5ec43d5abfd49cfe421cadedbbe665140582b0a','tests/external-tools-ui.test.tsx':'97ffbc70e29d4ff60a48e5aabd0ff3faec6dea7984ed0f239fcb4a8fc868f4d3'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected frozen hashes.
- [ ] `npx vitest run tests/release-detail.test.tsx tests/studio-workspace.test.tsx` passes.
- [ ] `git diff -- components/studio-workspace/use-studio-workspace-controller.ts components/studio-workspace/release-composer.tsx tests/legacy-capability-surface.test.ts tests/arch024-preview-cleanup.test.ts` is empty.

- [ ] `npm test` passes without task-introduced regression.
- [ ] `npm run typecheck` passes.
- [ ] targeted `npm run lint -- <changed Commerce source/test files>` (or repository-equivalent targeted ESLint invocation using the declared lint script) passes.
- [ ] `npm run build` succeeds.
- [ ] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Commerce task.

## Implementation Notes

None

## Completion Report

### Status

Ready for Review

### Files Changed

- `components/studio-workspace.tsx`
- `components/studio-workspace/release-detail.tsx`
- `tests/release-detail.test.tsx`

### Work Completed

- Extracted the complete Release Detail presentation and local activation/rollback confirmation state into `release-detail.tsx`; preserved the `StudioWorkspace` and `StudioPage` exports and existing router/controller boundaries.
- Preserved role-independent edit-as-new handoff, operation ID generation, members, cloned response contract, validation hash, blank reason, return route and clone navigation.
- Preserved SUPER_ADMIN activation/rollback gates, ADMIN copy, rollback label, required reason and expected active-pointer version payloads. Reason edits still mark global dirty and Cancel does not clear it.
- Added four focused tests covering clone handoff, activation payload, rollback payload and dirty/cancel behavior.
- Controller, Release Composer, frozen tests, source scanners and other out-of-scope files were not changed.

### Validation Results

- Prepared worktrees were used as supplied: parent and implementation branch `task/ARCH-025-COMMERCE-003`; both were clean at entry. Implementation HEAD already contained `origin/main`; no worktree preparation, synchronization, claim, or submodule initialization was repeated. Node `v24.19.0` was available through the approved workspace runtime.
- `npm ci` installed locked dependencies. It emitted peer/deprecation/audit and install-script approval warnings; no dependency manifests or lockfiles were changed.
- `npx vitest run tests/release-detail.test.tsx`: passed, 4/4.
- Required `npx vitest run tests/release-detail.test.tsx tests/studio-workspace.test.tsx`: new Release Detail tests passed; StudioWorkspace reported the same 6 known failures and 11 passes. The 6 failures are documented by `ARCH025-COMMERCE-TEST-001` and are in unchanged `tests/studio-workspace.test.tsx`.
- Frozen suite `npx vitest run tests/studio-workspace.test.tsx tests/agent-configuration-screen-state.test.tsx tests/external-tools-ui.test.tsx`: 2 files passed, 1 file failed; 6 known StudioWorkspace failures and 108 passes. All three frozen SHA-256 hashes match the task's expected values.
- `git diff --exit-code -- components/studio-workspace/use-studio-workspace-controller.ts components/studio-workspace/release-composer.tsx tests/legacy-capability-surface.test.ts tests/arch024-preview-cleanup.test.ts`: passed; no changes.
- `npm run typecheck`: passed after Prisma client generation.
- `npm run lint -- components/studio-workspace.tsx components/studio-workspace/release-detail.tsx tests/release-detail.test.tsx`: passed with 0 errors; 2 existing hook warnings in `src/studio/code-response/code-response-panel.tsx`.
- Production build steps passed: manuals package/smoke, code-runtime package/smoke, `npx prisma generate --schema database/prisma/schema.prisma`, and `npx next build --webpack`. Prisma was generated directly from the already-prepared submodule; the build script's recursive submodule update was intentionally not run. Next completed compilation, TypeScript, page generation and build traces with existing Nunjucks critical-dependency warnings.
- `git diff --check`: passed.
- Full `npm test` after Prisma generation: 21 failed files / 31 failed tests, 139 passed files / 1,353 passed tests, 5 skipped files / 9 skipped tests. Aggregate results are better than the documented accepted baseline (`ARCH025-COMMERCE-TEST-001`: 23 failed files / 38 failed tests, 135 passed files / 1,335 passed tests, 5 skipped files / 9 skipped tests); the focused frozen Studio failures match the documented identities. The suite is not reported as passing.

### Deviations

- `npm run build` was represented by its declared build steps with Prisma generation invoked directly, because the package script begins with `git submodule update --init --recursive`, which would repeat the explicitly prohibited submodule initialization. The equivalent production build completed successfully.

### Assumptions

The six frozen StudioWorkspace failures are the inherited failures documented in `ARCH025-COMMERCE-TEST-001`; the matching focused result, unchanged frozen hashes, and improved full-suite aggregate show no task-introduced regression.

### Unresolved Issues

- The frozen StudioWorkspace tests and full Commerce suite retain documented baseline failures; architect review should treat the test acceptance checkbox above as baseline-limited rather than fully green.

### Architectural Concerns

None.

## Architect Review

### Attempt 1 Review Status

Changes Requested — Attempt 1

### Attempt 1 Review Notes

The Release Detail extraction is architecture-conformant on source inspection and no Release Detail implementation correction is requested at this stage. Direct comparison with the accepted COMMERCE-002 `StudioWorkspace` implementation shows that the extracted clone, activation/rollback, role-gating, active-pointer fencing and dirty/cancel workflow is a faithful structural move. The shell change removes the local Release Detail implementation/imports and imports the dedicated module without changing the public `StudioWorkspace` / `StudioPage` boundary.

All three frozen assets retain their required SHA-256 values. `use-studio-workspace-controller.ts`, `release-composer.tsx`, `tests/legacy-capability-surface.test.ts` and `tests/arch024-preview-cleanup.test.ts` remain unchanged as required. The four focused Release Detail tests cover edit-as-new handoff, activation, rollback and dirty/cancel semantics.

Acceptance is withheld for deterministic baseline classification and execution evidence, not for a discovered Release Detail source defect.

**A1-R1 — classify the complete package-wide failure set against `ARCH025-COMMERCE-TEST-001` and reconcile the required checkboxes.**

The task correctly cites the six frozen `tests/studio-workspace.test.tsx` failures as documented baseline identities, but the full `npm test` result is recorded only as aggregate counts (`21` failed files / `31` failed tests). `ARCH025-COMMERCE-TEST-001` permits later tasks to rely on the durable baseline only when the observed failures are a subset of the stable failing test/collection identities with equivalent reasons. Improved aggregate totals alone do not prove that condition.

Attempt 2 MUST record the exact failing test identities and collection failures from the submitted full-suite run and compare them against `ARCH025-COMMERCE-TEST-001`. Any new, changed or worsened identity must be investigated as a possible COMMERCE-003 regression. If every observed failure is baseline-covered with equivalent reason, or an out-of-baseline failure is investigated and shown unrelated/non-reproducible, no implementation source change is required.

Once that evidence is recorded, update the task-owned Acceptance Criteria and Validation checkboxes consistently: baseline-covered frozen/package-wide commands may be marked satisfied as **no task-introduced regression**, with the baseline ID and exact evidence recorded. Do not describe the known baseline suite as literally green.

**A1-R2 — record the launcher-resolved physical-isolation, synchronization and recursive-submodule packet.**

The Completion Report currently says prepared worktrees were supplied and that synchronization/claim/submodule initialization were not repeated, but it does not durably record the preparation packet required by the architect protocol.

Attempt 2 MUST record the actual prepared-execution evidence, including:

- canonical `workspace_root`;
- dedicated parent task worktree path and `task/ARCH-025-COMMERCE-003` branch;
- dedicated Commerce implementation worktree path and matching task branch;
- confirmation that the shared/default checkout and another task's worktree were not used for task edits;
- parent task-branch synchronization result and `origin/main` incorporation state;
- implementation task-branch synchronization result and `origin/main` incorporation state;
- dependency gate proving `ARCH-025-COMMERCE-002` Complete;
- `git submodule sync --recursive` and `git submodule update --init --recursive` preparation evidence;
- exact `database` gitlink identity;
- Attempt 2 claim metadata and durable claim commit;
- submitted implementation head and `origin/task/ARCH-025-COMMERCE-003` equality;
- final parent report head and matching remote task head;
- final clean status for both worktrees.

A matching launcher packet is valid start-of-attempt evidence; do not rerun preparation merely to manufacture output if the packet already exists. This is evidence-only. Do not create implementation churn solely to produce a new source commit.

### Attempt 1 Reviewed Files

- `components/studio-workspace.tsx`
- `components/studio-workspace/release-detail.tsx`
- `tests/release-detail.test.tsx`
- protected COMMERCE-001 controller/scanner and COMMERCE-002 Release Composer files
- frozen StudioWorkspace / Agent Configuration / External Tools UI assets
- `docs/development-baseline.md`
- COMMERCE-003 Completion Report

### Attempt 1 Validation Reviewed

- Release Detail focused tests: 4/4 passed.
- Required Release Detail + StudioWorkspace run: four new Release Detail tests passed; six documented frozen StudioWorkspace failures remained.
- Frozen three-file suite: 108 passed; the same six documented StudioWorkspace failures remained.
- Frozen SHA-256 checks: all matched.
- Protected-file diff gate: passed.
- Typecheck: passed.
- Targeted lint: passed with only two existing warnings in untouched Code Response source.
- Production build: passed with existing Nunjucks warning.
- `git diff --check`: passed.
- Full `npm test`: improved aggregate of 21 failed files / 31 failed tests / 1,353 passed / 9 skipped, but exact failure identities were not recorded against the durable baseline and therefore require Attempt 2 evidence.

### Attempt 1 Architecture Conformance

Implementation conformance is satisfactory. Review remains open only because the baseline/no-regression gate and required execution packet are not yet durably proven in the task report.

### Attempt 1 Follow-up

Return the same task to its configured execution path for Attempt 2. Prefer an evidence/report-only retry. Change Release Detail source only if exact failure-identity classification demonstrates a new COMMERCE-003-owned regression. Do not start `ARCH-025-COMMERCE-004`.
