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
status: complete
priority: 20
executor: null
claimed_at: null
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
- [x] Frozen 13/3/90-test assets remain byte-identical. The exact focused run has four Release Detail tests pass and the same six known StudioWorkspace failures documented in `ARCH025-COMMERCE-TEST-001`; no task-owned focused failure was found.


## Validation

- [x] Frozen-hash `node -e ...` check prints all three expected hashes.
- [x] `npx vitest run tests/release-detail.test.tsx tests/studio-workspace.test.tsx`: 4 Release Detail tests and 11 StudioWorkspace tests pass; only the six documented baseline StudioWorkspace tests fail.
- [x] `git diff --exit-code -- components/studio-workspace/use-studio-workspace-controller.ts components/studio-workspace/release-composer.tsx tests/legacy-capability-surface.test.ts tests/arch024-preview-cleanup.test.ts` is empty.

- [x] `npm test` has no demonstrated task-introduced regression relative to `ARCH025-COMMERCE-TEST-001`; exact identities, collection errors and non-reproduced outliers are recorded below. The suite is not literally green.
- [x] `npm run typecheck` passes.
- [x] targeted `npm run lint -- <changed Commerce source/test files>` passes.
- [x] Production build succeeds.
- [x] `git diff --check` passes.

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
- Attempt 2 was evidence-only. Architect A1-R1 was addressed by comparing the complete current full-suite identity set to `ARCH025-COMMERCE-TEST-001`; no Release Detail source correction was indicated. Architect A1-R2 was addressed by recording the prepared launcher packet below.

### Validation Results

- Attempt 2 launcher packet: canonical `workspace_root` `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; dedicated parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-COMMERCE-003` and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-COMMERCE-003`, both on `task/ARCH-025-COMMERCE-003`. The shared/default checkout and another task's worktree were not used for task edits.
- Attempt 2 synchronization packet: parent task-branch fast-forward `not-needed`, `origin/main` incorporation `yes`, synchronized parent head `713db9cc41f4125fbefce85ec33060034a36332b`; implementation task-branch fast-forward `not-needed`, `origin/main` incorporation `already-current`, submitted implementation head `7af250d8781ad821d576a31a0f0054b28f1f3754`. Dependency `ARCH-025-COMMERCE-002` passed as `complete`.
- Recursive submodule preparation: launcher `git submodule sync --recursive` passed and `git submodule update --init --recursive` passed. Database gitlink is `cfeeb12456b4e05067a96857a8c47837d7e33bbd`, initialized at that exact commit.
- Attempt 2 claim: executor `copilot`, timestamp `2026-10-03T01:54:13Z`, attempt 2 (from attempt 1), durable parent claim commit `d16e3e857e89f28926be4725b8b0bdc834656260`, committed and pushed. No additional source or implementation commit was created in Attempt 2. Implementation HEAD and `origin/task/ARCH-025-COMMERCE-003` both equal `7af250d8781ad821d576a31a0f0054b28f1f3754`.
- `npm ci` installed locked dependencies during Attempt 1; it emitted peer/deprecation/audit and install-script approval warnings. Attempt 2 used the prepared existing dependency tree and approved Node `v24.19.0`; no dependency manifests or lockfiles were changed.
- `npx vitest run tests/release-detail.test.tsx`: passed, 4/4 in Attempt 1.
- Attempt 2 exact focused command `npx vitest run tests/release-detail.test.tsx tests/studio-workspace.test.tsx`: 1 file passed / 1 failed; 4 Release Detail and 11 StudioWorkspace tests passed, with only the six frozen StudioWorkspace failures. Their exact test names match `ARCH025-COMMERCE-TEST-001`.
- Frozen suite `npx vitest run tests/studio-workspace.test.tsx tests/agent-configuration-screen-state.test.tsx tests/external-tools-ui.test.tsx`: 2 files passed, 1 file failed; 6 known StudioWorkspace failures and 108 passes. All three frozen SHA-256 hashes match the task's expected values.
- `git diff --exit-code -- components/studio-workspace/use-studio-workspace-controller.ts components/studio-workspace/release-composer.tsx tests/legacy-capability-surface.test.ts tests/arch024-preview-cleanup.test.ts`: passed; no changes.
- `npm run typecheck`: passed after Prisma client generation.
- `npm run lint -- components/studio-workspace.tsx components/studio-workspace/release-detail.tsx tests/release-detail.test.tsx`: passed with 0 errors; 2 existing hook warnings in `src/studio/code-response/code-response-panel.tsx`.
- Production build steps passed: manuals package/smoke, code-runtime package/smoke, `npx prisma generate --schema database/prisma/schema.prisma`, and `npx next build --webpack`. Prisma was generated directly from the already-prepared submodule; the build script's recursive submodule update was intentionally not run. Next completed compilation, TypeScript, page generation and build traces with existing Nunjucks critical-dependency warnings.
- `git diff --check`: passed.
- Attempt 2 full `npm test` on unchanged submitted head `7af250d8781ad821d576a31a0f0054b28f1f3754`: 23 failed files / 34 failed tests, 137 passed files / 1,350 passed tests, 5 skipped files / 9 skipped tests (165 files / 1,393 tests total). The exact six collection failures are the baseline's `agent-configuration-model-postgres.test.ts`, `agent-configuration-prompts-postgres.test.ts`, `c20-integration-fixture.test.ts`, `local-external-mcp-diagnostic.test.ts`, `preview-openrouter-postgres.test.ts`, and `studio-integration-c20.test.ts`; their reasons remain equivalent: disposable PostgreSQL/Redis/C20 environment variables are absent, or the diagnostic is required to run via its declared script.
- Exact test-identity comparison against the 33 stable identities in `ARCH025-COMMERCE-TEST-001`: 31 stable identities recur. The two stable External Tools UI identities not present in this run are `does not create a live-test receipt from Automatic generation and keeps publication gated` and `traverses new external tool authoring through U06, U14, return context and publish`. The three additional observed identities are `tests/discovery-process.test.ts > initializes, lists actual tools, performs an approved call, and closes` (MCP request timed out in the full run), `tests/external-tools-ui.test.tsx > stales persisted Test on argument and shop changes without persistence writes` (15-second test timeout), and `tests/readiness-docker.test.ts > kills ignored-stdio descendants after leader exit on abort` (descendant readiness file was not observed before cancellation). Each exact case passed in an isolated rerun under the same pinned runtime (1/1 each); the unchanged owners are respectively the Shopify MCP process test, the frozen External Tools UI suite, and readiness child-process test, none touched by this task. These are classified as investigated, non-reproduced run variance, not blanket baseline exemptions. The other 31 current test identities are stable baseline entries. Disappeared baseline failures were not recreated.
- `ARCH025-COMMERCE-TEST-001` records all 33 stable identities by exact file and test name; the current set is exactly that stable set minus the two named identities above, plus the three individually non-reproduced identities above. Current six frozen Studio failures are the same six names recorded in that baseline. No task-owned Release Detail test failed, and the full suite remains non-green.

### Deviations

- `npm run build` was represented by its declared build steps with Prisma generation invoked directly, because the package script begins with `git submodule update --init --recursive`, which would repeat the explicitly prohibited submodule initialization. The equivalent production build completed successfully.

### Assumptions

The six frozen StudioWorkspace failures are the inherited failures documented in `ARCH025-COMMERCE-TEST-001`; the matching focused result, unchanged frozen hashes, and improved full-suite aggregate show no task-introduced regression.

### Unresolved Issues

- The full suite remains non-green. Attempt 2's three out-of-stable-set full-run failures passed individually; exact identities and reasons are recorded above. No new or task-owned reproducible failure was established.

### Attempt 2 Architect Requests

- A1-R1: implemented as evidence-only. Compared the full suite against `ARCH025-COMMERCE-TEST-001`, listed the exact delta, recorded all six collection identities/reasons, and isolated all three out-of-stable-set cases; none reproduced individually. Focused Release Detail validation remains green apart from the six named frozen Studio baseline failures.
- A1-R2: implemented as evidence-only. The canonical workspace, both dedicated worktrees/branches, synchronization states, dependency gate, recursive submodule operations and identity, Attempt 2 claim, submitted implementation/remote equality, and final post-publication clean/remote-equal worktrees are recorded in this report and verified after publication.

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

### Attempt 2 Review Status

Accepted — Attempt 2

### Attempt 2 Review Notes

The evidence-only retry closes both Attempt 1 review findings. The submitted Commerce implementation remains exactly the reviewed Attempt 1 implementation (`7af250d8781ad821d576a31a0f0054b28f1f3754`); no Release Detail source/test change was made in Attempt 2. The Release Detail extraction therefore remains a faithful move-only refactor preserving edit-as-new handoff, SUPER_ADMIN activation/rollback gating, active-pointer fencing, dirty-on-reason and cancel-does-not-clear-dirty semantics.

`ARCH025-COMMERCE-TEST-001` now governs the broad-suite result deterministically: 31 stable failing test identities recur; two stable External Tools UI identities disappear and are treated as improvement; the three additional full-run identities are outside COMMERCE-003 ownership and each passes its exact isolated rerun under the same pinned runtime. All six collection failures retain baseline-equivalent environment/declared-script causes. No Release Detail-owned focused test fails and no new baseline exemption is created.

The Completion Report also records the required launcher-resolved dedicated parent/implementation worktrees, start-of-attempt synchronization, dependency gate, recursive submodule preparation, exact database gitlink, durable Attempt 2 claim, submitted implementation/remote equality and clean remote-aligned final worktrees.

### Attempt 2 Reviewed Files

- `components/studio-workspace.tsx`
- `components/studio-workspace/release-detail.tsx`
- `tests/release-detail.test.tsx`
- `docs/development-baseline.md` (`ARCH025-COMMERCE-TEST-001`)
- `docs/decisions/commerce/ARCH-025/COMMERCE-003-extract-release-detail.md`

### Attempt 2 Validation Reviewed

- Focused Release Detail / frozen Studio command: 4 Release Detail + 11 StudioWorkspace tests pass; only the six exact documented StudioWorkspace baseline failures remain.
- Frozen integration/state suite: 108 pass; only the same six documented StudioWorkspace failures remain; all three required SHA-256 hashes match.
- Protected COMMERCE-001 controller / COMMERCE-002 Release Composer / source-scanner diff check: clean.
- Full `npm test`: 1,350 passed, 34 failed, 9 skipped; 31 stable baseline identities recur, two stable identities disappear, and all three out-of-baseline full-run outliers pass isolated reruns.
- Typecheck, targeted lint, production build and `git diff --check`: pass as recorded in the Completion Report.

### Attempt 2 Architecture Conformance

Accepted. The implementation conforms to the parent architecture, COMMERCE-003 scope, frozen/protected-owner constraints and `ARCH025-COMMERCE-TEST-001` no-regression rules. No source correction or baseline expansion is required.

### Attempt 2 Follow-up

`ARCH-025-COMMERCE-004` is promoted to `ready`. Do not begin it implicitly as part of this review.
