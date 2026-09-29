---
id: ARCH-021-COMMERCE-094
architecture_id: ARCH-021
title: Resolve Commerce production build TypeScript diagnostics
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 9
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-021-COMMERCE-093
enables:
  - ARCH-021-COMMERCE-086
created: 2026-09-29
updated: 2026-09-29
---

# Resolve Commerce production build TypeScript diagnostics

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Resolve the bounded set of TypeScript diagnostics preventing the Commerce production build from completing, then prove the normal production build passes. Do not broaden this into unrelated cleanup or change runtime behavior beyond what is necessary to make the reported code type-safe.

## Context

ARCH-021-COMMERCE-093 corrects three over-deep imports in:

```text
app/api/studio/code-response/validate/route.ts
```

After those imports resolve, the normal `npm run build` advances to Next.js type validation and fails with 23 TypeScript diagnostics across 12 files. The diagnostic files observed on 2026-09-29 are:

```text
scripts/validate-shopify-admin-local.ts
src/studio/discovery/admin-query-builder.ts
src/studio/tools/authoring/result-template-tab.tsx
tests/admin-query-execution.test.ts
tests/agent-configuration-effective.test.ts
tests/agent-configuration-prompts-postgres.test.ts
tests/c20-integration-fixture.test.ts
tests/local-external-mcp-diagnostic.test.ts
tests/result-template-tab.test.tsx
tests/selected-shop-context.test.ts
tests/shopify-admin-live-test.test.ts
tests/tool-result-contract.test.ts
```

The current diagnostic output is recorded in the preceding C093 Attempt 1 Completion Report. These defects are outside C093's route-import scope. This task is the production-build prerequisite for C086's clean build and static-manual HTTP smoke.

## Scope

Implementation repository:

```text
moda-interact-commerce/
```

Attempt 1/2 established that all diagnostics in the original 12-file C093-era baseline are resolved.

For Attempt 3, the allowed implementation boundary is explicitly expanded to include exactly the three newly exposed project-wide blocker files below in addition to the already-authorized C094 files:

```text
src/commerce/execution/renderer.ts
tests/add-capability-screen.test.tsx
tests/feature-authoring.test.ts
```

The current 19 diagnostics are:
- 2 renderer narrowing errors reading `operation` / `operationVersion` from the wrong execution variant;
- 16 test typing errors reading `disabled` from values typed only as `HTMLElement`;
- 1 Feature-authoring fixture typing error where the mocked `featureModel.findUnique` result is incomplete for the current selected shape.

Do not broaden beyond these three newly authorized files and the original C094 file set. Do not modify C086 packaging, manual source, or guide-link files except where an existing diagnostic in the already-authorized Result Template files requires a strictly minimal type correction.

## Out of Scope

- Changing the three route imports fixed by C093.
- C086 manual packaging, manual content, build lifecycle integration, or guide-link behavior, except minimal type corrections required to resolve diagnostics in the listed files.
- Unrelated TypeScript cleanup outside the enumerated diagnostic sites.
- Broad changes to TypeScript compiler options, lint rules, or strictness.
- Adding `@ts-ignore`, `@ts-nocheck`, unsafe casts, blanket suppressions, or disabling type checking to make the build pass.
- Runtime behavior changes not required to make the reported code type-safe.
- Database schema, generated Prisma model, dependency, or lockfile changes.

## Requirements

### R1 — resolve the observed diagnostic set

Use the current branch's actual compiler output as authoritative because diagnostics may shift after synchronization and accepted ARCH-021 work.

Attempts 1 and 2 resolved the complete original 12-file diagnostic set. Attempt 3 is authorized to resolve the current remaining 19 diagnostics only in:

```text
src/commerce/execution/renderer.ts
tests/add-capability-screen.test.tsx
tests/feature-authoring.test.ts
```

If `npx tsc --noEmit --pretty false` exposes a new diagnostic outside the original C094 files plus these three explicitly authorized files, do not fix it opportunistically; stop and return the exact blocker to `moda_architect`.

### R2 — preserve runtime behavior

Make type-correct implementation changes that preserve existing runtime contracts. Prefer correct narrowing, annotations, and compatible test fixtures over weakening types or suppressing diagnostics.

### R3 — normal production build passes

Run the repository-declared command from a clean generated state as appropriate:

```text
npm run build
```

Acceptance requires exit code zero. Record the full command outcome. If an unrelated build failure outside this task's bounded diagnostic set appears, do not fix it here; report the exact blocker to `moda_architect`.

### R4 — unblock C086 without doing C086

Do not start C086 Attempt 2. `moda_architect` must accept C093 and C094 and explicitly return C086 to Ready before its next authorized claim. C086 then owns its own clean-build and production-start HTTP smoke.

## Work Items

- [x] Run TypeScript diagnostics and reconcile the current errors with the 12-file baseline recorded by C093.
- [x] Correct the locally resolvable type errors in the enumerated files, preserving runtime behavior.
- [x] Attempt 3: resolve the 19 current diagnostics in the three newly authorized blocker files, preserving runtime/test semantics.
- [x] Add or adjust focused tests only when needed to substantiate changed behavior or type-safe fixtures.
- [x] Run targeted ESLint for changed files.
- [x] Run `npx tsc --noEmit --pretty false` and verify there are no remaining project diagnostics.
- [x] Run `git diff --check`.
- [x] Run the normal `npm run build` and require success.
- [x] Complete the report with changed files, validations, and any remaining out-of-scope blocker.

## Dependencies

- ARCH-021-COMMERCE-093

## Enables

- ARCH-021-COMMERCE-086

## Acceptance Criteria

- [x] The listed TypeScript diagnostics are resolved without suppressing type checking or adding blanket ignores.
- [x] Runtime behavior remains unchanged except for necessary type-safe corrections.
- [x] Changes remain limited to the listed files and directly required focused tests.
- [x] Attempt 3 changes remain limited to the original C094 scope plus `src/commerce/execution/renderer.ts`, `tests/add-capability-screen.test.tsx`, and `tests/feature-authoring.test.ts`.
- [x] Targeted lint passes for changed files.
- [x] `npx tsc --noEmit --pretty false` passes with no diagnostics.
- [x] `git diff --check` passes.
- [x] Normal `npm run build` succeeds.
- [x] No C086 Attempt 2 or production-start smoke is performed by this task.

## Validation

- [x] Inspect actual TypeScript diagnostics after C093 is accepted.
- [x] Targeted ESLint for changed files.
- [x] `npx tsc --noEmit --pretty false`.
- [x] `git diff --check`.
- [x] `npm run build`.

## Stop Condition

After all Work Items, Acceptance Criteria, and Validation items pass, set this task to `review`, complete the Completion Report, and stop. Do not begin C086 Attempt 2.

## Completion Report

### Status

Ready for Architect Review after Attempt 3. The full project typecheck and normal production build pass.

### Files Changed

Implementation files:

- `scripts/validate-shopify-admin-local.ts`
- `src/studio/discovery/admin-query-builder.ts`
- `src/studio/tools/authoring/result-template-tab.tsx`
- `tests/admin-query-execution.test.ts`
- `tests/agent-configuration-effective.test.ts`
- `tests/agent-configuration-prompts-postgres.test.ts`
- `tests/local-external-mcp-diagnostic.test.ts`
- `tests/result-template-tab.test.tsx`
- `tests/selected-shop-context.test.ts`
- `tests/shopify-admin-live-test.test.ts`
- `tests/tool-result-contract.test.ts`
- `tests/add-capability-screen.test.tsx`
- `tests/feature-authoring.test.ts`

### Work Completed

Corrected type narrowing in GraphQL AST construction and result-schema rendering; aligned fixture types with the Commerce result/template contracts; corrected nullable result assertions and prompt-result test narrowing; updated selected-shop tests to use the current server-action-backed API. No runtime contract was intentionally changed.

Attempt 2 first found stale generated dependencies in the reused implementation worktree: `package.json` and `package-lock.json` pin Shared 1.0.0, but `node_modules` contained 0.14.2. `npm ci` restored the locked package and `npm run prisma:generate` regenerated Prisma Client from the pinned schema. With that corrected state, all diagnostics in C094's 12-file baseline are gone, but project-wide checking still reports 19 errors in three out-of-scope files: `src/commerce/execution/renderer.ts` (2 errors reading `operation` and `operationVersion` from an `EXTERNAL_HTTP` definition), `tests/add-capability-screen.test.tsx` (16 errors reading `disabled` from `HTMLElement`), and `tests/feature-authoring.test.ts` (1 incomplete `featureModel.findUnique` mock result). These are outside the task's allowed implementation files. No out-of-scope source, dependency declaration/lockfile, compiler configuration, database schema, or submodule pointer was changed.

Attempt 3 used the Architect's expanded three-file boundary. The synchronized current baseline already had the renderer's policy-operation narrowing correction, so that file produced no current diagnostic and required no Attempt 3 edit. In `tests/add-capability-screen.test.tsx`, a runtime-checked `HTMLButtonElement` helper makes the existing disabled-state assertions type-safe without weakening them. In `tests/feature-authoring.test.ts`, the mocked Feature now returns the complete selected Feature shape. No runtime behavior changed.

Prepared execution evidence:

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-094`, branch `task/ARCH-021-COMMERCE-094`
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-094`, branch `task/ARCH-021-COMMERCE-094`
- Shared workspace and implementation checkouts were not switched or edited; no other task worktree was reused.
- The prepared launcher synchronized both task branches and initialized recursive submodules; the `database` submodule remained at `e9fb60221f1532205650154dfff2aadb6270b14c`.
- Attempt 2 claim: executor `copilot`, claim commit `042e8121d23d93f7e70559247b679e1e6d644124`, pushed. Implementation task commit from Attempt 1 is `b6e9ac0e9223a90cdcb3d3eb037c909b37afc44b`; current `main` incorporation is merge commit `d04cf146a9c801f1f3a265bc553ae5fd2cb209bc`.
- Attempt 3 claim: executor `copilot`, claim commit `cb20e427974bf606b251e0585348a5173c2224ca`, pushed. Prepared parent head after synchronization: `8101bebff4dd8d79e45383a102da23d5fefe4854`; implementation baseline after synchronization: `a36731f4503ac011aedbca9d043380257c52c271`.

### Validation Results

Passed:

- `npx eslint scripts/validate-shopify-admin-local.ts src/studio/discovery/admin-query-builder.ts src/studio/tools/authoring/result-template-tab.tsx tests/admin-query-execution.test.ts tests/agent-configuration-effective.test.ts tests/agent-configuration-prompts-postgres.test.ts tests/local-external-mcp-diagnostic.test.ts tests/result-template-tab.test.tsx tests/selected-shop-context.test.ts tests/shopify-admin-live-test.test.ts tests/tool-result-contract.test.ts`
- Attempt 2 targeted ESLint: zero errors, one warning (`capabilityDraft` unused in `tests/local-external-mcp-diagnostic.test.ts`).
- Attempt 3 targeted ESLint across the original C094 files and all three newly authorized files: passed with no diagnostics.
- Focused Vitest suites: 48 tests passed across `tests/admin-query-execution.test.ts`, `tests/agent-configuration-effective.test.ts`, `tests/result-template-tab.test.tsx`, `tests/selected-shop-context.test.ts`, `tests/tool-result-contract.test.ts`, and `tests/shopify-admin-live-test.test.ts`.
- Attempt 3 focused Vitest packet across those six suites plus `tests/add-capability-screen.test.tsx` and `tests/feature-authoring.test.ts`: 61/61 passed.
- `git diff --check`
- `npm run prisma:generate` completed using the task-pinned database submodule.
- Attempt 2 `npm ci` restored the lockfile-pinned `@modainteract/moda-interact-shared@1.0.0`; generated dependency files were not added to the source diff.
- Attempt 3 `npx tsc --noEmit --pretty false`: passed with zero diagnostics after the production build refreshed stale Next.js route types.
- Attempt 3 `npm run build`: passed end to end, including code-runtime packaging/smoke, Prisma generation, TypeScript validation, static page generation and build trace finalization. Next.js emitted the existing Nunjucks critical-dependency warning during compilation.

Blocked:

- None in Attempt 3. The temporary `.next/types` references to deleted capability pages disappeared when `npm run build` regenerated Next.js artifacts; final standalone `tsc` passed.

### Deviations

The Architect expanded the implementation boundary for Attempt 3 to the three previously failing files. The synchronized renderer fix plus two focused test typing corrections resolved the remaining diagnostics. C086 Attempt 2 and its production-start smoke were not started.

### Assumptions

The dependency lockfile and generated Prisma Client are authoritative. The Next.js build refreshes stale route type artifacts before final standalone TypeScript validation.

### Unresolved Issues

None. The Attempt 1 missing-Prisma diagnosis was superseded after correcting the stale installed Shared package; the Attempt 2 three-file blocker was resolved under the Architect-approved Attempt 3 scope.

### Architectural Concerns

The project-wide typecheck and production build now pass with the narrowly authorized Attempt 3 corrections. C086 Attempt 2 and its production-start HTTP smoke were not started.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 3 is accepted.

C094 now satisfies its complete production-build gate. Attempts 1 and 2 resolved the original C093-era diagnostic set and identified the final 19 project-wide diagnostics. Attempt 3 used the architect-approved three-file scope expansion, with no further scope growth.

The synchronized baseline already contained the renderer union-narrowing correction, so no renderer edit was required in Attempt 3. The remaining two test-only corrections are appropriately narrow:

- `tests/add-capability-screen.test.tsx` now uses a runtime-checked `HTMLButtonElement` helper so the existing disabled-state assertions remain semantically identical while being type-correct;
- `tests/feature-authoring.test.ts` now returns the complete selected Feature shape required by the current persistence contract.

No TypeScript suppressions, compiler-option changes, Prisma/schema changes, dependency-manifest changes, C086 changes, or unrelated runtime behavior changes were introduced.

The validation gate is now fully green:

- global `npx tsc --noEmit --pretty false` completes with zero diagnostics;
- targeted ESLint passes;
- the focused packet passes 61/61;
- `git diff --check` passes;
- the normal `npm run build` completes successfully end to end, including code-runtime packaging/smoke, Prisma generation, TypeScript validation, static page generation and trace finalization.

The Nunjucks critical-dependency message emitted during compilation is a non-fatal build warning; the production build exits successfully.

C086 Attempt 2 and its production-start HTTP smoke were not started, preserving the task boundary.

### Reviewed Files

- `src/commerce/execution/renderer.ts`
- `tests/add-capability-screen.test.tsx`
- `tests/feature-authoring.test.ts`
- original C094 diagnostic-bearing source/test files listed in the task
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

### Validation Reviewed

- Attempt 3 focused packet: 61/61 passed.
- Global `npx tsc --noEmit --pretty false`: passed with zero diagnostics.
- Targeted ESLint across C094 changed files: passed.
- `git diff --check`: passed.
- `npm run build`: passed end to end.
- Prisma generation: passed.
- Code-runtime packaging/smoke within production build: passed.
- Nunjucks critical-dependency warning: non-fatal; build completed successfully.
- C086 Attempt 2 / production-start smoke: not started, as required.

### Architecture Conformance

Conforms.

C094 remains a bounded Commerce-repository build/type-safety correction. The final fixes preserve runtime semantics and restore the required project-wide typecheck and production-build prerequisites without altering ARCH-021 ownership, schema, Feature/Capability architecture or C086 behavior.

### Follow-up

ARCH-021-COMMERCE-094 is Complete.

ARCH-021-COMMERCE-086 is promoted from Blocked to Ready. C086 may now be reclaimed for Attempt 2 and owns its clean-build confirmation plus production-start HTTP smoke for the packaged Result Template guide.

Do not treat C094 acceptance itself as execution of C086.
