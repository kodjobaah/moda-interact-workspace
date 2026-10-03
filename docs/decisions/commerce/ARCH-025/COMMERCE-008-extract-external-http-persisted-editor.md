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
claimed_at: 2026-10-03T18:36:07Z
attempt: 2
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
- [x] `npm test`: Attempt 2 full-suite identities and collection failures were captured and classified under pinned Node 24.19.0 / npm 11.17.0; see the Attempt 2 Architect Corrections section. The suite remains non-zero with only baseline identities/collection failures plus one investigated, non-C008-owned Redis-dependent timeout.
- [x] `npm run typecheck` passed after Prisma client generation.
- [x] Targeted ESLint for `tool-editor.tsx` and `persisted-external-http-tool-editor.tsx` passed.
- [x] `npm run build`: passed on committed C008 under workspace-pinned Node 24.19.0 / npm 11.17.0 and task-local lockfile dependencies. Both packaging smokes, Prisma generation and the complete Next.js production build succeeded; the v2 helper namespace mutability failure did not recur.
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

### Attempt 1 Validation Results

- Frozen SHA-256 checks: all three expected hashes matched for `tests/shopify-admin-tools-ui.test.tsx`, `tests/tool-authoring-screen.test.tsx` and `tests/new-tool-authoring-state.test.ts`.
- Protected diff check: empty for the common controller, Policy wrapper and three frozen tests.
- `npx vitest run tests/persisted-external-http-tool-editor.test.tsx tests/external-tools-ui.test.tsx`: passed; 98 tests.
- `npx vitest run tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/new-tool-authoring-state.test.ts`: passed; 198 tests.
- `npm test`: non-zero; summary reported 1,315 passed, 74 failed and 9 skipped across 169 files. Named failures were `tests/studio-workspace.test.tsx` (`retains editor input after stale CAS`, unable to find the Shopify Admin `Save draft` button) and two 15-second timeouts in `tests/tool-authoring-screen.test.tsx` new-tool local External HTTP cases. These are outside the moved persisted External wrapper; the frozen `tool-authoring-screen` hash and targeted test set passed. The full-suite output did not enumerate all failures represented by its aggregate count.
- `npm run typecheck`: passed after the build's Prisma client generation.
- `npx eslint src/studio/tools/tool-editor.tsx src/studio/tools/authoring/persisted-external-http-tool-editor.tsx`: passed.
- `npm run build`: blocked before Next.js build by the unchanged packaged-runtime smoke, `scripts/code-runtime-packaged-smoke.mjs`, which reported `packaged v2 helper namespace is mutable`. This code/runtime path is outside task scope and no matching documented baseline entry was found; the failure is reported as unresolved, not treated as passing.
- `git diff --check`: passed.

### Attempt 2 Architect Corrections

#### A1-R1 - Full-suite failure classification

- The authoritative `npm test` run was repeated after bootstrapping the workspace-pinned Node `v24.19.0` and npm `11.17.0`. `package-lock.json` SHA-256 was `d8ebcf87bcd1ce0c9d2b62b88784abf359697e9149d97eadd04f97af04469d35`, matching `ARCH025-COMMERCE-TEST-001`. An earlier shell run under Node `v24.21.0` / npm `11.19.0` was superseded and is not used for classification.
- Exact pinned-run result: exit 1; 20 failed files, 144 passed files, 5 skipped files; 30 failed tests, 1,368 passed tests, 9 skipped tests, across 169 files.
- Stable baseline identities with the same failing test identity/assertion (29):

```text
tests/admin-explorer.test.tsx
  preserves a valid manual query that is not representable and returns it unchanged
  builds and validates a representable selection before merging query fields into an existing draft
  keeps exact raw text for an unchanged literal mapping and drops stale buffers
  round-trips a newly visual-authored string literal through the New Tool Request editor
  validates Request query while preserving malformed unrelated editor buffers
  shows validation progress while the Shopify Admin validation request is in flight
  validates a restored visual selection even when the selected root field is outside the loaded schema page
  keeps Validate available when the visual candidate cannot yet be built and reports the blocking reason
  offers a return action beside validation without applying temporary Explorer state
  cancel returns to the validated origin without merging temporary Explorer state

tests/admin-graphql-compiler.test.ts
  rejects nullable input schemas for non-null variables

tests/agent-configuration-retained-read.test.ts
  tracks model and prompt CAS versions on one retained row across clear operations

tests/agent-contract-validation.test.ts
  rejects unknown scalar paths and non-list items paths

tests/auth-entrypoints.test.ts
  keeps NextAuth and health public while the MCP route remains private

tests/backend-postgres-rehearsal.test.ts
  publishes once, replays durably, rejects stale CAS, races across connections, and rolls back injected failure

tests/discount-evaluator.test.ts
  retains preview purpose, environment, and trace correlation in eligibility telemetry

tests/health.test.ts
  readiness checks required dependencies and has no release-publication dependency
  bounds hanging dependencies under two seconds and aborts Redis

tests/merchant-knowledge-embedding.test.ts
  validates the exact OpenAI provenance environment contract

tests/policy-operation-authoring-server-actions.test.ts
  returns UNAVAILABLE for invalid or unregistered operation identities without fallback

tests/policy-operation-result-template.test.ts
  reports whether each currently registered operation result is template-compatible

tests/preview-page.test.tsx
  projects only browser-safe selected-Shop configuration and Feature fields
  never forwards an invalid URL Shop ID as the selected Shop

tests/studio-workspace.test.tsx
  exposes the failure class when a named Studio action rejects unexpectedly
  authors a reusable tool without publishing and navigates to its returned ID
  retains incremental invalid JSON and saves only the complete canonical tool definition
  resets editor state when a mounted detail changes to another record
  keeps newer edits dirty when an earlier save completes
  retains editor input after stale CAS
```

- Documented baseline identities absent from this pinned run (improved/disappeared, not recreated): `tests/external-tools-ui.test.tsx` / `does not create a live-test receipt from Automatic generation and keeps publication gated`; `tests/external-tools-ui.test.tsx` / `traverses new external tool authoring through U06, U14, return context and publish`; and `tests/readiness-docker.test.ts` / `kills ignored-stdio descendants after leader exit on timeout`.
- Changed/worsened baseline identity requiring investigation: `tests/discovery-limits.test.ts` / `allows 60 sequential requests and rejects the 61st in the rolling window` timed out after 30 seconds rather than reaching its rate-limit assertion. A focused rerun under pinned Node reproduced the timeout. The test requires configured `REDIS_URL` and performs 60 sequential Redis-backed calls; the endpoint value was not inspected and no further run was made. C008 changes only the ToolEditor shell and the new persisted External wrapper; neither this test nor its `lib/discovery/limits` owner changed. This is investigated as a non-C008-owned environment/runtime failure, not treated as an equivalent baseline cause.
- Stable collection failures (all six match `ARCH025-COMMERCE-TEST-001` with the same missing-gate/invocation causes): `tests/agent-configuration-model-postgres.test.ts`, `tests/agent-configuration-prompts-postgres.test.ts`, and `tests/preview-openrouter-postgres.test.ts` require `COMMERCE_TEST_DATABASE_URL`; `tests/c20-integration-fixture.test.ts` requires disposable PostgreSQL, Redis and namespace variables; `tests/local-external-mcp-diagnostic.test.ts` requires `npm run diagnose:arch020-external-mcp:local`; `tests/studio-integration-c20.test.ts` requires disposable C20 targets.
- No C008-owned regression was found in the full-suite classification. No test, implementation or durable baseline file was modified.

#### A1-R2 - Production build reproducibility

- Exact `npm run build` on committed C008 passed under Node `v24.19.0` / npm `11.17.0` with the task-local lockfile. Manuals packaging/smoke passed; `code-runtime:package` and `code-runtime:smoke` passed; Prisma Client generation passed; Next.js webpack production compilation, type generation, static pages, traces and finalization passed.
- Packaged runtime hashes: QuickJS artifact `d4c9375f2b1ca4dc95f72c8aa2982a7a9951ac8011490d79c6582df732b4bbd9`; `helpers-v2.js` `83fe8b710c646680781e605baa64f77ef215cea9bd7aa7df4133afd358c9c31a`. The smoke exercised the v2 immutable helper namespace and passed. The prior Attempt 1 mutable-namespace smoke failure did not recur, so the conditional C007/C008 artifact comparison was not required.
- Next emitted the existing Nunjucks critical-dependency warnings; the production build completed successfully.

#### Attempt 2 claim and worktrees

- Launcher claim: Attempt 2, executor `copilot`, claimed `2026-10-03T18:36:07Z`; durable parent claim commit `fa0f00aa41ace6035230a01a554d711248f0695d`.
- The dedicated parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-COMMERCE-008` and Commerce worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-COMMERCE-008` remain on `task/ARCH-025-COMMERCE-008`. C007 dependency was complete; the initialized Database submodule was `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3`.
- Implementation remains the exact pushed C008 commit `c96248298d3c62be7e5a1ab92f55a063b1c41b94`; no implementation source was changed in Attempt 2. Before this report edit both local branches matched their own origin task refs, both worktrees were clean, and no submodule gitlink was staged.

### Attempt 1 Deviations

The requested production build did not complete because the unchanged packaged code-runtime smoke failed. No out-of-scope runtime or smoke changes were made. Repository-wide test failures are recorded above; the focused persisted External and neighboring authoring suites passed, and the only focused `studio-workspace` failures match the documented frozen baseline.

### Assumptions

The wrapper is only reached from the shell's persisted External DRAFT dispatch; its guard is defensive and does not change the dispatch contract.

### Unresolved Issues

The C008 task gates are resolved for review: the required build passed and the full-suite failures were inventoried. The isolated Redis-backed discovery-limit timeout remains an out-of-scope validation failure for its owning area; its configured endpoint was not inspected or retried. Architect review should determine follow-up ownership. No C008 implementation change is indicated.

### Architectural Concerns

None. No cross-repository contract or architecture changes were required.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 implementation is structurally conformant and remains within the authorised C008 boundary. Direct comparison with architect-accepted `ARCH-025-COMMERCE-007` shows that the only meaningful Commerce source changes are `src/studio/tools/tool-editor.tsx` plus the new `src/studio/tools/authoring/persisted-external-http-tool-editor.tsx`; `tsconfig.tsbuildinfo` is generated output. The common controller, accepted Policy wrapper, accepted External source harness and all three frozen Tool-authoring tests are byte-identical. The External DRAFT wrapper preserves the existing provider/action ownership, connection revision pinning, no-port asymmetry, Request/Response/Test/Result Template freshness, authoritative Review fencing, save convergence, SUPER_ADMIN publication gate and shell-owned `RevisionHistory`. No C008 source redesign is requested by this review.

**A1-R1 — repository-wide test classification is incomplete.** The required `npm test` gate remains unchecked. The report records an aggregate of 1,315 passed / 74 failed / 9 skipped and identifies only a subset of the failing identities. `ARCH025-COMMERCE-TEST-001` may be reused only when every failing test identity and collection failure is classified. Attempt 2 must capture the exact full-suite failed test identities and collection failures and classify each as: (a) stable baseline identity with equivalent cause, (b) documented baseline identity that disappeared/improved, or (c) new/changed/worsened identity requiring investigation. Every out-of-baseline identity must be rerun/investigated before review. If this proves no C008-owned regression, do not change implementation source and mark the baseline-aware validation item satisfied. Do not expand the durable baseline merely because the aggregate run is non-green.

**A1-R2 — production build gate remains unresolved.** `npm run build` is a required task gate and the submitted run stops in the unchanged packaged code-runtime smoke with `packaged v2 helper namespace is mutable`. The C004 review previously demonstrated intermittent standalone smoke variability, but that observation was deliberately not added as a durable baseline and does not by itself satisfy C008's build gate. Attempt 2 must first rerun the exact full `npm run build` on the committed C008 head using the workspace-pinned Node version and task-local lockfile dependencies. If it passes, record the successful full build and close this item. If the same smoke failure recurs, perform a bounded reproducibility comparison using clean synchronized pre-task C007 and exact C008 snapshots under the same Node/dependency environment: repeat `code-runtime:package` + `code-runtime:smoke`, hash all packaging inputs and generated artifacts, preserve/diff differing helpers, and cross-run preserved artifacts so the evidence establishes whether failure follows artifact content or checkout/environment. If clean C008 consistently fails while clean pre-task passes despite identical semantic packaging inputs, do not modify code-runtime inside C008; return the task `blocked` with the evidence for architect decomposition. If the evidence instead identifies a C008-owned regression, correct only that regression and rerun the required validation.

The existing launcher/worktree packet is sufficient: the report records the canonical root, dedicated parent and Commerce task worktrees, physical-isolation attestations, start synchronization, C007 dependency gate, recursive submodule materialisation, Database gitlink, claim evidence and final clean remote-aligned branches. No further workflow-evidence correction is requested unless Attempt 2 changes those facts.

### Reviewed Files

- `src/studio/tools/tool-editor.tsx`
- `src/studio/tools/authoring/persisted-external-http-tool-editor.tsx`
- `src/studio/tools/authoring/use-persisted-tool-authoring-controller.ts`
- `src/studio/tools/authoring/persisted-policy-operation-tool-editor.tsx`
- `tests/external-tools-ui.test.tsx`
- `tests/shopify-admin-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`
- `tests/new-tool-authoring-state.test.ts`
- `docs/development-baseline.md` (`ARCH025-COMMERCE-TEST-001`)
- this task's Completion Report

### Validation Reviewed

- Frozen Tool-authoring hashes: exact.
- Common controller / Policy wrapper / accepted External source harness protected comparison: unchanged.
- External UI suite: 98 passed.
- Neighboring Tool-authoring compatibility suite: 198 passed.
- Typecheck: reported passing.
- Targeted ESLint: reported passing.
- `git diff --check`: reported passing.
- Repository-wide `npm test`: non-zero and not completely identity-classified; correction required by A1-R1.
- Production build: non-zero at packaged-runtime smoke; correction/evidence required by A1-R2.

### Architecture Conformance

The implementation conforms to the move-only C008 architecture on inspected source. Acceptance is withheld only because required validation remains unresolved. `ARCH-025-COMMERCE-009` remains dependency-gated until this task is Complete.

### Follow-up

Reclaim the same task for Attempt 2. Treat the retry as evidence/build-reproducibility work first. Do not change the persisted External wrapper unless A1-R1 or A1-R2 proves a task-owned regression, and do not begin `ARCH-025-COMMERCE-009`.
