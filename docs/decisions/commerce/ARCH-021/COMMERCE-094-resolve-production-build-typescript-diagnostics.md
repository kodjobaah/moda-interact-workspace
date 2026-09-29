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
status: in_progress
priority: 9
executor: copilot
claimed_at: 2026-09-29T19:24:37Z
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
- [ ] Attempt 3: resolve the 19 current diagnostics in the three newly authorized blocker files, preserving runtime/test semantics.
- [x] Add or adjust focused tests only when needed to substantiate changed behavior or type-safe fixtures.
- [x] Run targeted ESLint for changed files.
- [ ] Run `npx tsc --noEmit --pretty false` and verify there are no remaining project diagnostics.
- [x] Run `git diff --check`.
- [ ] Run the normal `npm run build` and require success.
- [x] Complete the report with changed files, validations, and any remaining out-of-scope blocker.

## Dependencies

- ARCH-021-COMMERCE-093

## Enables

- ARCH-021-COMMERCE-086

## Acceptance Criteria

- [x] The listed TypeScript diagnostics are resolved without suppressing type checking or adding blanket ignores.
- [x] Runtime behavior remains unchanged except for necessary type-safe corrections.
- [x] Changes remain limited to the listed files and directly required focused tests.
- [ ] Attempt 3 changes remain limited to the original C094 scope plus `src/commerce/execution/renderer.ts`, `tests/add-capability-screen.test.tsx`, and `tests/feature-authoring.test.ts`.
- [x] Targeted lint passes for changed files.
- [ ] `npx tsc --noEmit --pretty false` passes with no diagnostics.
- [x] `git diff --check` passes.
- [ ] Normal `npm run build` succeeds.
- [x] No C086 Attempt 2 or production-start smoke is performed by this task.

## Validation

- [x] Inspect actual TypeScript diagnostics after C093 is accepted.
- [x] Targeted ESLint for changed files.
- [ ] `npx tsc --noEmit --pretty false`.
- [x] `git diff --check`.
- [ ] `npm run build`.

## Stop Condition

After all Work Items, Acceptance Criteria, and Validation items pass, set this task to `review`, complete the Completion Report, and stop. Do not begin C086 Attempt 2.

## Completion Report

### Status

Blocked on Attempt 2; not submitted for Architect Review because the required project typecheck and production build remain blocked by TypeScript errors in files outside C094's implementation-file boundary.

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

### Work Completed

Corrected type narrowing in GraphQL AST construction and result-schema rendering; aligned fixture types with the Commerce result/template contracts; corrected nullable result assertions and prompt-result test narrowing; updated selected-shop tests to use the current server-action-backed API. No runtime contract was intentionally changed.

Attempt 2 first found stale generated dependencies in the reused implementation worktree: `package.json` and `package-lock.json` pin Shared 1.0.0, but `node_modules` contained 0.14.2. `npm ci` restored the locked package and `npm run prisma:generate` regenerated Prisma Client from the pinned schema. With that corrected state, all diagnostics in C094's 12-file baseline are gone, but project-wide checking still reports 19 errors in three out-of-scope files: `src/commerce/execution/renderer.ts` (2 errors reading `operation` and `operationVersion` from an `EXTERNAL_HTTP` definition), `tests/add-capability-screen.test.tsx` (16 errors reading `disabled` from `HTMLElement`), and `tests/feature-authoring.test.ts` (1 incomplete `featureModel.findUnique` mock result). These are outside the task's allowed implementation files. No out-of-scope source, dependency declaration/lockfile, compiler configuration, database schema, or submodule pointer was changed.

Prepared execution evidence:

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-094`, branch `task/ARCH-021-COMMERCE-094`
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-094`, branch `task/ARCH-021-COMMERCE-094`
- Shared workspace and implementation checkouts were not switched or edited; no other task worktree was reused.
- The prepared launcher synchronized both task branches and initialized recursive submodules; the `database` submodule remained at `e9fb60221f1532205650154dfff2aadb6270b14c`.
- Attempt 2 claim: executor `copilot`, claim commit `042e8121d23d93f7e70559247b679e1e6d644124`, pushed. Implementation task commit from Attempt 1 is `b6e9ac0e9223a90cdcb3d3eb037c909b37afc44b`; current `main` incorporation is merge commit `d04cf146a9c801f1f3a265bc553ae5fd2cb209bc`.

### Validation Results

Passed:

- `npx eslint scripts/validate-shopify-admin-local.ts src/studio/discovery/admin-query-builder.ts src/studio/tools/authoring/result-template-tab.tsx tests/admin-query-execution.test.ts tests/agent-configuration-effective.test.ts tests/agent-configuration-prompts-postgres.test.ts tests/local-external-mcp-diagnostic.test.ts tests/result-template-tab.test.tsx tests/selected-shop-context.test.ts tests/shopify-admin-live-test.test.ts tests/tool-result-contract.test.ts`
- Attempt 2 targeted ESLint: zero errors, one warning (`capabilityDraft` unused in `tests/local-external-mcp-diagnostic.test.ts`).
- Focused Vitest suites: 48 tests passed across `tests/admin-query-execution.test.ts`, `tests/agent-configuration-effective.test.ts`, `tests/result-template-tab.test.tsx`, `tests/selected-shop-context.test.ts`, `tests/tool-result-contract.test.ts`, and `tests/shopify-admin-live-test.test.ts`.
- `git diff --check`
- `npm run prisma:generate` completed using the task-pinned database submodule.
- Attempt 2 `npm ci` restored the lockfile-pinned `@modainteract/moda-interact-shared@1.0.0`; generated dependency files were not added to the source diff.

Blocked:

- Attempt 2 `npx tsc --noEmit --pretty false`: 19 errors in three files, all outside this task's allowed implementation set: `src/commerce/execution/renderer.ts` (2), `tests/add-capability-screen.test.tsx` (16), and `tests/feature-authoring.test.ts` (1). No diagnostics remained in C094's 12-file baseline.
- Attempt 2 `npm run build`: code-runtime packaging and packaged smoke passed; Prisma Client generation passed; Next.js production compilation passed with a Nunjucks critical-dependency warning; the build then failed during TypeScript validation on the same 19 errors. Exit code was nonzero.

### Deviations

Required project-wide typecheck and normal production build could not pass without editing the three out-of-scope diagnostic files or expanding this task's implementation boundary. The task remains `blocked`, not `review`; Attempt 2 did not start C086 or its production-start smoke.

### Assumptions

The dependency lockfile and generated Prisma Client are authoritative for this attempt. Remaining errors must be fixed by their owning task(s), or the Architect must explicitly expand C094's allowed file set before implementation continues.

### Unresolved Issues

`moda_architect` must coordinate ownership of the three remaining diagnostic files or explicitly re-scope C094 before the global typecheck/build criteria can be met. The previous Attempt 1 diagnosis of missing ARCH-021 Prisma models was not reproduced after correcting the stale installed Shared package; it is superseded by Attempt 2's current compiler output.

### Architectural Concerns

The original C093-era diagnostics in C094's allowed files are resolved, but the production build remains blocked by 19 project-wide type errors outside the task boundary. C086 Attempt 2 and its production-start HTTP smoke were not started.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 2 correctly resolved every diagnostic in C094's original 12-file boundary and demonstrated that the earlier missing-Prisma-model diagnosis was caused by stale installed dependencies rather than the current ARCH-021 schema/client.

The remaining production-build blocker is now bounded to 19 TypeScript diagnostics in exactly three Commerce-owned files outside the original task boundary:

```text
src/commerce/execution/renderer.ts          2
tests/add-capability-screen.test.tsx       16
tests/feature-authoring.test.ts             1
```

These errors belong naturally to C094's existing bounded outcome—restore a clean repository typecheck and production build before C086 resumes. Creating a second build-unblocker task would artificially split one repository-owned validation gate. The C094 implementation boundary is therefore expanded narrowly for Attempt 3.

#### A2-R1 — resolve the current 19 diagnostics in the three newly authorized files

Authorized files:

```text
src/commerce/execution/renderer.ts
tests/add-capability-screen.test.tsx
tests/feature-authoring.test.ts
```

Correction requirements:

- In `renderer.ts`, correct execution-union narrowing so POLICY_OPERATION-only fields (`operation`, `operationVersion`) are accessed only after proving the policy execution variant. Preserve renderer behavior and existing template/result contracts.
- In `tests/add-capability-screen.test.tsx`, make button disabled-state assertions type-correct without weakening assertions or using unsafe casts/suppressions. Prefer Testing Library/Jest-DOM semantics or an appropriate element type.
- In `tests/feature-authoring.test.ts`, update the fake `featureModel.findUnique` result so it satisfies the current selected Feature shape used by the production persistence path. Preserve the test's intended behavior.
- Do not change Prisma schema, generated model definitions, TypeScript compiler options, lint rules, dependency manifests/lockfiles, C086 files, or unrelated runtime behavior.
- Do not add `@ts-ignore`, `@ts-nocheck`, blanket suppressions, or unsafe `any` escapes merely to silence the compiler.

After the corrections:

1. run focused tests covering the three corrected sites plus the existing C094 focused packet as appropriate;
2. run targeted ESLint over all C094-changed files;
3. run `npx tsc --noEmit --pretty false` and require zero diagnostics;
4. run `git diff --check`;
5. run the normal `npm run build` and require exit code zero;
6. reconcile the Completion Report;
7. return C094 to `review`, clear the claim, and STOP.

Do not start C086 Attempt 2 or its production-start smoke. C086 remains blocked until C094 is architect-accepted Complete.

### Reviewed Files

- `src/commerce/execution/renderer.ts`
- `tests/add-capability-screen.test.tsx`
- `tests/feature-authoring.test.ts`
- C094 task Completion Report and Attempt-2 validation evidence
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

### Validation Reviewed

- Original C094 diagnostic set: resolved.
- Focused C094 tests: 48/48 passed.
- Targeted ESLint: zero errors, one documented unused-variable warning.
- Prisma generation: passed.
- Code-runtime packaging and packaged smoke during `npm run build`: passed.
- Next.js production compilation: passed before TypeScript validation.
- Current global TypeScript blocker: 19 diagnostics in the three newly authorized files.
- Current production build blocker: the same 19 TypeScript diagnostics.
- `git diff --check`: passed.

### Architecture Conformance

C094 remains the correct repository-owned production-build gate. The three-file scope expansion is a bounded type-safety correction and does not change ARCH-021 runtime ownership or Feature/Capability architecture.

### Follow-up

Return the same task through `/moda-task` for Attempt 3. Execute A2-R1 only, satisfy the global typecheck and production-build criteria, return to `review`, clear the claim, and STOP.
