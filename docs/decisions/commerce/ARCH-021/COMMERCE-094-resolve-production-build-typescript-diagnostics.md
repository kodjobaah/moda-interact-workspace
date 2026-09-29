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
status: blocked
priority: 9
executor: null
claimed_at: null
attempt: 2
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

Allowed implementation files are limited to the 12 diagnostic-bearing files listed above, plus focused tests only if a reported source diagnostic requires a test adjustment. Do not modify C086 packaging, manual source, or guide-link files except where an existing diagnostic in the listed Result Template files requires a strictly minimal type correction.

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

Use the current branch's actual compiler output as authoritative because diagnostics may shift after C093 is accepted. Resolve only the diagnostics in the 12 listed files that prevent the required build from passing. Do not assume the original count remains exactly 23 after code changes.

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

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
